#!/usr/bin/env python3
"""Emmy Kernel IR -> PTX.

    python compile.py path/to/kernel.ir.json > out.ptx

Pipeline:
  1. load    - Graph.from_dict gives the typed KernelOp; meta.json (next to the IR) gives
               the parameter order, buffer shapes and launch geometry.
  2. prescan - collect shared arrays, written buffers and Init-declared accumulators.
  3. walk    - one s_<Kind> method per IR statement appends PTX lines; expressions are
               compiled recursively by expr(). `env` maps IR names to registers.
  4. emit    - header, shared declarations, signature, register declarations, body.

Registers are virtual and fresh (%f float, %r 32-bit int, %rd 64-bit address, %p predicate);
ptxas does the real allocation.
"""

from __future__ import annotations

import json
import math
import struct
import sys
from pathlib import Path

from emmy.compiler.graph import Graph

PTX_VERSION, TARGET = "8.0", "sm_89"
STATIC_SMEM_LIMIT = 48 * 1024           # above this, shared arrays live in one dynamic pool
UNROLL_LIMIT = 4096                     # max statements emitted when honoring Loop.unroll
SMEM_BYTES = {"float": 4, "f32": 4}
LOG2E, LN2 = "0f3FB8AA3B", "0f3F317218"


class Unsupported(Exception):
    pass


def f32(x: float) -> str:
    """PTX hex literal for an f32 constant."""
    return "0f%08X" % struct.unpack("<I", struct.pack("<f", float(x)))[0]


def is_imm(x: str) -> bool:
    return not x.startswith("%")


def dim(d) -> int:
    """Static extent of an Axis' Dim."""
    e = d.expr
    if type(e).__name__ != "Literal":
        raise Unsupported(f"dynamic extent {d!r}")
    return int(e.value)


def c_div(a: int, b: int) -> int:     # C semantics: truncate toward zero
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b > 0) else -q


# emmy renders "//" as C "/" (truncating), so both lower to div.s32
INT_BIN = {"+": "add.s32", "-": "sub.s32", "*": "mul.lo.s32", "/": "div.s32", "//": "div.s32",
           "%": "rem.s32", "<<": "shl.b32", ">>": "shr.s32", "&": "and.b32", "|": "or.b32", "^": "xor.b32",
           "min": "min.s32", "max": "max.s32"}
INT_CMP = {"<": "lt", "<=": "le", ">": "gt", ">=": "ge", "==": "eq", "!=": "ne"}
PRED_BIN = {"&&": "and.pred", "and": "and.pred", "||": "or.pred", "or": "or.pred"}
FOLD = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b,
        "/": c_div, "//": c_div, "%": lambda a, b: a - b * c_div(a, b), "<<": lambda a, b: a << b,
        ">>": lambda a, b: a >> b, "&": lambda a, b: a & b, "|": lambda a, b: a | b,
        "^": lambda a, b: a ^ b, "min": min, "max": max,
        "<": lambda a, b: int(a < b), "<=": lambda a, b: int(a <= b), ">": lambda a, b: int(a > b),
        ">=": lambda a, b: int(a >= b), "==": lambda a, b: int(a == b), "!=": lambda a, b: int(a != b)}

# Elementwise ops with a one-instruction lowering.
F_BIN = {"add": "add.f32", "subtract": "sub.f32", "multiply": "mul.f32", "divide": "div.rn.f32",
         "true_divide": "div.rn.f32", "maximum": "max.f32", "minimum": "min.f32"}
F_UN = {"copy": "mov.f32", "negative": "neg.f32", "abs": "abs.f32", "absolute": "abs.f32",
        "reciprocal": "rcp.rn.f32", "sqrt": "sqrt.rn.f32", "rsqrt": "rsqrt.approx.f32",
        "floor": "cvt.rmi.f32.f32", "ceil": "cvt.rpi.f32.f32", "trunc": "cvt.rzi.f32.f32",
        "round": "cvt.rni.f32.f32", "rint": "cvt.rni.f32.f32",
        "sin": "sin.approx.f32", "cos": "cos.approx.f32", "exp2": "ex2.approx.f32",
        "log2": "lg2.approx.f32"}


def fmt(e) -> str:
    """Expression as short ASCII text, for PTX comments."""
    t = type(e).__name__
    if t == "Var":
        return e.name
    if t == "Literal":
        return repr(e.value)
    if t == "BinaryExpr":
        return f"({fmt(e.left)} {e.op} {fmt(e.right)})"
    if t == "TernaryExpr":
        return f"({fmt(e.cond)} ? {fmt(e.if_true)} : {fmt(e.if_false)})"
    return t


def idx(index) -> str:
    return "[" + ", ".join(fmt(i) for i in index) + "]"


class Kernel:
    def __init__(self, op, karg: list[dict], launch: dict):
        self.op, self.karg, self.launch = op, karg, launch
        self.lines: list[str] = []
        self.n = {"p": 0, "r": 0, "rd": 0, "f": 0}
        self.nlabel = 0
        self.env: dict[str, str] = {}     # IR name -> register or immediate
        self.kind: dict[str, str] = {}    # IR name -> register class
        self.bufs: dict[str, dict] = {}   # buffer name -> space/base/shape/bytes
        self.smem: list[tuple[str, int, int]] = []
        self.declared: set[str] = set()   # accumulators seeded by Init
        self.acc_owner: dict[str, str] = {}   # accumulator -> loop axis that seeded it
        self.written: set[str] = set()

    # ---- small helpers ---------------------------------------------------
    def new(self, k: str) -> str:
        self.n[k] += 1
        return f"%{k}{self.n[k]}"

    def label(self, hint: str) -> str:
        self.nlabel += 1
        return f"$L{self.nlabel}_{hint}"

    def emit(self, s: str) -> None:
        self.lines.append("\t" + s)

    def comment(self, s: str) -> None:
        self.lines.append("\t// " + s.encode("ascii", "replace").decode())

    def bind(self, name: str, reg: str, k: str) -> None:
        self.env[name], self.kind[name] = reg, k

    def dest(self, name: str, k: str = "f") -> str:
        """Register for a value being (re)defined: reuse the name's register so loop-carried
        redefinitions (accumulators, shuffle ladders) update in place."""
        r = self.env.get(name)
        if r is None or is_imm(r) or self.kind[name] != k:
            r = self.new(k)
            self.bind(name, r, k)
        return r

    def val(self, name: str) -> str:
        if name not in self.env:
            raise Unsupported(f"value {name!r} used before definition")
        return self.env[name]

    def reg(self, x: str, k: str = "r") -> str:
        """Materialize an immediate into a register (some operand slots need one)."""
        if not is_imm(x):
            return x
        r = self.new(k)
        self.emit(f"mov.{'s32' if k == 'r' else 'f32'} {r}, {x};")
        return r

    # ---- integer expressions ---------------------------------------------
    def iop(self, op: str, a: str, b: str) -> tuple[str, str]:
        if is_imm(a) and is_imm(b) and op in FOLD:
            return str(FOLD[op](int(a), int(b))), "r"
        if op in ("+", "-") and b == "0" or op in ("*", "/") and b == "1":
            return a, "r"
        if op == "+" and a == "0" or op == "*" and a == "1":
            return b, "r"
        if op == "*" and "0" in (a, b):
            return "0", "r"
        if op in INT_CMP:
            p = self.new("p")
            self.emit(f"setp.{INT_CMP[op]}.s32 {p}, {self.reg(a)}, {b};")
            return p, "p"
        if op not in INT_BIN:
            raise Unsupported(f"integer operator {op!r}")
        if is_imm(a) and op in ("+", "*", "&", "|", "^", "min", "max"):
            a, b = b, a
        d = self.new("r")
        self.emit(f"{INT_BIN[op]} {d}, {self.reg(a)}, {b};")
        return d, "r"

    def expr(self, e) -> tuple[str, str]:
        t = type(e).__name__
        if t == "Literal":
            if isinstance(e.value, float) and not float(e.value).is_integer():
                return f32(e.value), "f"
            return str(int(e.value)), "r"
        if t == "Var":
            return self.val(e.name), self.kind[e.name]
        if t == "BinaryExpr":
            if e.op in PRED_BIN:
                a, b = self.pred(e.left), self.pred(e.right)
                p = self.new("p")
                self.emit(f"{PRED_BIN[e.op]} {p}, {a}, {b};")
                return p, "p"
            (a, ka), (b, kb) = self.expr(e.left), self.expr(e.right)
            if "f" in (ka, kb) or "p" in (ka, kb):
                raise Unsupported(f"non-integer operands in {fmt(e)}")
            return self.iop(e.op, a, b)
        if t == "TernaryExpr":
            c = self.pred(e.cond)
            (a, _), (b, _) = self.expr(e.if_true), self.expr(e.if_false)
            if c in ("0", "1"):
                return (a if c == "1" else b), "r"
            d = self.new("r")
            self.emit(f"selp.s32 {d}, {a}, {b}, {c};")
            return d, "r"
        raise Unsupported(f"expression {t}")

    def pred(self, e) -> str:
        x, k = self.expr(e)
        if k == "p":
            return x
        if is_imm(x):
            return "1" if int(x) else "0"
        p = self.new("p")
        self.emit(f"setp.ne.s32 {p}, {x}, 0;")
        return p

    # ---- addressing --------------------------------------------------------
    def offset(self, index, shape) -> str:
        """Row-major element offset of `index` in a buffer of `shape`."""
        index, shape = list(index), list(shape)
        if not index:
            return "0"
        shape = shape[len(shape) - len(index):] if len(shape) >= len(index) else \
            [1] * (len(index) - len(shape)) + shape
        off, stride = "0", 1
        for i, ext in zip(reversed(index), reversed(shape)):
            term, _ = self.iop("*", self.expr(i)[0], str(stride))
            off, _ = self.iop("+", off, term)
            stride *= ext
        return off

    def address(self, buf: str, off: str) -> tuple[str, int]:
        """(base register or symbol, byte displacement) of element `off` of `buf`."""
        b = self.bufs.get(buf)
        if b is None:
            raise Unsupported(f"unknown buffer {buf!r}")
        eb = b["bytes"]
        if b["space"] == "global":
            if is_imm(off):
                return b["base"], int(off) * eb
            w, a = self.new("rd"), self.new("rd")
            self.emit(f"mul.wide.s32 {w}, {off}, {eb};")
            self.emit(f"add.s64 {a}, {b['base']}, {w};")
            return a, 0
        if is_imm(off):
            return b["sym"], b["pool_off"] + int(off) * eb
        a = self.new("r")
        self.emit(f"mad.lo.s32 {a}, {off}, {eb}, {self.smem_base(buf)};")
        return a, 0

    def smem_base(self, buf: str) -> str:
        return self.bufs[buf]["reg"]     # set in the prologue: valid on every path

    @staticmethod
    def at(base: str, disp: int) -> str:
        return f"[{base}+{disp}]" if disp else f"[{base}]"

    def space(self, buf: str) -> str:
        return self.bufs[buf]["space"]

    # ---- elementwise -------------------------------------------------------
    def elementwise(self, name: str, d: str, args: list[str]) -> None:
        """d = name(args) for f32 values; composites write d last so d may alias an arg."""
        E = self.emit
        if name in F_BIN:
            E(f"{F_BIN[name]} {d}, {args[0]}, {args[1]};")
        elif name in F_UN:
            E(f"{F_UN[name]} {d}, {args[0]};")
        elif name in ("exp", "exp_fast"):
            t = self.new("f")
            E(f"mul.f32 {t}, {args[0]}, {LOG2E};")
            E(f"ex2.approx.f32 {d}, {t};")
        elif name == "log":
            t = self.new("f")
            E(f"lg2.approx.f32 {t}, {args[0]};")
            E(f"mul.f32 {d}, {t}, {LN2};")
        elif name == "relu":
            E(f"max.f32 {d}, {args[0]}, 0f00000000;")
        elif name == "square":
            E(f"mul.f32 {d}, {args[0]}, {args[0]};")
        elif name in ("sigmoid", "silu"):
            t = self.new("f")
            self.elementwise("negative", t, args)
            self.elementwise("exp", t, [t])
            E(f"add.f32 {t}, {t}, 0f3F800000;")
            if name == "sigmoid":
                E(f"rcp.rn.f32 {d}, {t};")
            else:
                E(f"div.rn.f32 {d}, {args[0]}, {t};")
        elif name == "tanh":   # sign(x) * (1 - e) / (1 + e), e = exp(-2|x|)
            e, n, q = self.new("f"), self.new("f"), self.new("f")
            E(f"abs.f32 {e}, {args[0]};")
            E(f"mul.f32 {e}, {e}, 0fC0000000;")
            self.elementwise("exp", e, [e])
            E(f"sub.f32 {n}, 0f3F800000, {e};")
            E(f"add.f32 {e}, {e}, 0f3F800000;")
            E(f"div.rn.f32 {q}, {n}, {e};")
            E(f"copysign.f32 {d}, {args[0]}, {q};")
        elif name == "softplus":   # max(x, 0) + log(1 + exp(-|x|))
            t, m = self.new("f"), self.new("f")
            E(f"abs.f32 {t}, {args[0]};")
            E(f"neg.f32 {t}, {t};")
            self.elementwise("exp", t, [t])
            E(f"add.f32 {t}, {t}, 0f3F800000;")
            self.elementwise("log", t, [t])
            E(f"max.f32 {m}, {args[0]}, 0f00000000;")
            E(f"add.f32 {d}, {m}, {t};")
        elif name == "erf":   # Abramowitz-Stegun 7.1.26, |error| < 1.5e-7
            x, t, p, e = args[0], self.new("f"), self.new("f"), self.new("f")
            E(f"abs.f32 {t}, {x};")
            E(f"mul.f32 {e}, {t}, {t};")
            E(f"neg.f32 {e}, {e};")
            self.elementwise("exp", e, [e])
            E(f"fma.rn.f32 {t}, {t}, {f32(0.3275911)}, 0f3F800000;")
            E(f"rcp.rn.f32 {t}, {t};")
            E(f"mov.f32 {p}, {f32(1.061405429)};")
            for c in (-1.453152027, 1.421413741, -0.284496736, 0.254829592):
                E(f"fma.rn.f32 {p}, {p}, {t}, {f32(c)};")
            E(f"mul.f32 {p}, {p}, {t};")
            E(f"mul.f32 {p}, {p}, {e};")
            E(f"sub.f32 {p}, 0f3F800000, {p};")
            E(f"copysign.f32 {d}, {x}, {p};")
        elif name == "gelu":   # 0.5 x (1 + erf(x / sqrt 2))
            t = self.new("f")
            E(f"mul.f32 {t}, {args[0]}, {f32(1 / math.sqrt(2))};")
            self.elementwise("erf", t, [t])
            E(f"add.f32 {t}, {t}, 0f3F800000;")
            E(f"mul.f32 {t}, {t}, {args[0]};")
            E(f"mul.f32 {d}, {t}, 0f3F000000;")
        elif name == "gelu_tanh":   # 0.5 x (1 + tanh(sqrt(2/pi) (x + 0.044715 x^3)))
            x, t = args[0], self.new("f")
            E(f"mul.f32 {t}, {x}, {x};")
            E(f"fma.rn.f32 {t}, {t}, {f32(0.044715)}, 0f3F800000;")
            E(f"mul.f32 {t}, {t}, {x};")
            E(f"mul.f32 {t}, {t}, {f32(math.sqrt(2 / math.pi))};")
            self.elementwise("tanh", t, [t])
            E(f"add.f32 {t}, {t}, 0f3F800000;")
            E(f"mul.f32 {t}, {t}, {x};")
            E(f"mul.f32 {d}, {t}, 0f3F000000;")
        elif name in ("power", "pow"):   # |x|^y, sign fixed for odd integer y, 0^0 = 1
            x, y = args
            t, r, ip, q = self.new("f"), self.new("f"), self.new("f"), self.new("r")
            neg, odd, zero, pi = self.new("p"), self.new("p"), self.new("p"), self.new("p")
            E(f"abs.f32 {t}, {x};")
            E(f"lg2.approx.f32 {t}, {t};")
            E(f"mul.f32 {t}, {t}, {y};")
            E(f"ex2.approx.f32 {r}, {t};")
            E(f"cvt.rzi.f32.f32 {ip}, {y};")
            E(f"setp.eq.f32 {pi}, {ip}, {y};")
            E(f"cvt.rzi.s32.f32 {q}, {y};")
            E(f"and.b32 {q}, {q}, 1;")
            E(f"setp.eq.and.s32 {odd}, {q}, 1, {pi};")
            E(f"setp.lt.f32 {neg}, {x}, 0f00000000;")
            E(f"and.pred {odd}, {odd}, {neg};")
            E(f"@{odd} neg.f32 {r}, {r};")
            E(f"not.pred {pi}, {pi};")
            E(f"and.pred {neg}, {neg}, {pi};")
            E(f"@{neg} mov.f32 {r}, 0f7FFFFFFF;")
            E(f"setp.eq.f32 {zero}, {y}, 0f00000000;")
            E(f"selp.f32 {d}, 0f3F800000, {r}, {zero};")
        elif name == "where":
            p = self.new("p")
            E(f"setp.ne.f32 {p}, {args[0]}, 0f00000000;")
            E(f"selp.f32 {d}, {args[1]}, {args[2]}, {p};")
        else:
            raise Unsupported(f"elementwise op {name!r}")

    # ---- statements ----------------------------------------------------------
    def visit(self, body) -> None:
        for s in body:
            h = getattr(self, "s_" + type(s).__name__, None)
            if h is None:
                raise Unsupported(f"statement {type(s).__name__}")
            h(s)

    def s_Tile(self, s) -> None:
        if s.aux_threads:
            raise Unsupported("Tile with aux threads")
        exts = [dim(a.extent) for a in s.axes]
        n = self.tile_cells = math.prod(exts)
        self.comment(f"Tile[{', '.join(a.name for a in s.axes)}] (N={n})")
        gid = self.new("r")
        self.emit(f"mad.lo.s32 {gid}, {self.ctaid}, {self.ntid}, {self.tid};")
        end = self.label("tile_end")
        if n < math.prod(self.launch["grid"]) * math.prod(self.launch["block"]):
            p = self.new("p")
            self.emit(f"setp.ge.s32 {p}, {gid}, {n};      // guard: launch has more threads than cells")
            self.emit(f"@{p} bra {end};")
        strides = [math.prod(exts[i + 1:]) for i in range(len(exts))]
        for i, a in enumerate(s.axes):     # row-major: last axis fastest
            v, _ = self.iop("/", gid, str(strides[i]))
            if i:
                v, _ = self.iop("%", v, str(exts[i]))
            self.bind(a.name, v, "r")
        self.raster(s, exts, strides, gid)
        self.visit(s.body)
        self.lines.append(f"{end}:")

    def raster(self, s, exts, strides, gid) -> None:
        """Grouped CTA rasterization: G block-tiles of the grouped axis iterate fastest, so
        neighbouring CTAs share an operand slab. Rebinds the two raster axes."""
        names = [a.name for a in s.axes]
        if not (s.raster_group and s.raster_axes and all(r in names for r in s.raster_axes[:2])):
            return
        mi, ni = names.index(s.raster_axes[0]), names.index(s.raster_axes[1])
        if ni != mi + 1:
            return
        gi, oi = (mi, ni) if s.raster_orient == "m" else (ni, mi)
        g = min(s.raster_group, exts[gi])
        if exts[gi] <= 1 or g <= 1:
            return
        ea, eb = exts[gi], exts[oi]
        I = self.iop
        sub, _ = I("/", gid, str(strides[ni]))
        if mi:
            sub, _ = I("%", sub, str(ea * eb))
        grp, _ = I("/", sub, str(g * eb))
        within, _ = I("%", sub, str(g * eb))
        size = str(g)
        if ea % g:      # ragged last group: size = min(G, ea - grp*G)
            size, _ = I("min", str(g), I("-", str(ea), I("*", grp, str(g))[0])[0])
        av, _ = I("+", I("*", grp, str(g))[0], I("%", within, size)[0])
        bv, _ = I("/", within, size)
        self.bind(names[gi], av, "r")
        self.bind(names[oi], bv, "r")

    def s_Load(self, s) -> None:
        if s.dtype is not None and s.dtype.name != "f32":     # shared-memory loads carry no dtype
            raise Unsupported(f"load of {s.dtype.name}")
        self.comment(f"{', '.join(s.names)} = load {s.input}{idx(s.index)}")
        base, disp = self.address(s.input, self.offset(s.index, self.bufs[s.input]["shape"]))
        sp = self.space(s.input)
        op = "ld.global.nc" if sp == "global" and s.input not in self.written else f"ld.{sp}"
        regs = [self.dest(nm) for nm in s.names]
        if len(regs) in (2, 4):
            self.emit(f"{op}.v{len(regs)}.f32 {{{', '.join(regs)}}}, {self.at(base, disp)};")
        else:
            for i, r in enumerate(regs):
                self.emit(f"{op}.f32 {r}, {self.at(base, disp + 4 * i)};")

    def s_Write(self, s) -> None:
        if s.value_dtype.name != "f32" or s.swizzle != "NONE":
            raise Unsupported("write of non-f32 or swizzled values")
        self.comment(f"{s.output}{idx(s.index)} {'+=' if s.atomic else '='} ({', '.join(s.values)})")
        base, disp = self.address(s.output, self.offset(s.index, self.bufs[s.output]["shape"]))
        sp = self.space(s.output)
        vals = [self.reg(self.val(v), "f") for v in s.values]
        if s.atomic:
            for i, v in enumerate(vals):
                self.emit(f"red.{sp}.add.f32 {self.at(base, disp + 4 * i)}, {v};")
        elif len(vals) in (2, 4):
            self.emit(f"st.{sp}.v{len(vals)}.f32 {self.at(base, disp)}, {{{', '.join(vals)}}};")
        else:
            for i, v in enumerate(vals):
                self.emit(f"st.{sp}.f32 {self.at(base, disp + 4 * i)}, {v};")

    def s_Assign(self, s, comment: bool = True) -> None:
        if s.dtype is not None and s.dtype.name != "f32":
            raise Unsupported(f"assign of {s.dtype.name}")
        if comment:
            self.comment(f"{s.name} = {s.op.name}({', '.join(s.args)})")
        args = [self.val(a) for a in s.args]
        self.elementwise(s.op.name, self.dest(s.name), args)

    def s_Let(self, s) -> None:
        self.comment(f"{s.name} = {fmt(s.value)}")
        x, k = self.expr(s.value)
        if s.dtype is not None and s.dtype.name == "f32":
            if k == "r":
                x = f32(int(x)) if is_imm(x) else None
            if x is None:
                raise Unsupported("Let of a non-literal float")
            self.emit(f"mov.f32 {self.dest(s.name)}, {x};")
        else:
            self.bind(s.name, x, k)

    def s_Select(self, s) -> None:
        """name = value of the first branch whose predicate holds: a selp chain built backwards."""
        self.comment(f"{s.name} = select(" + ", ".join(f"{fmt(b.select)}: {b.value}" for b in s.branches) + ")")
        d, first = self.dest(s.name), True
        for b in reversed(s.branches):
            p, v = self.pred(b.select), self.val(b.value)
            if first or p == "1":
                self.emit(f"mov.f32 {d}, {v};")
            elif p != "0":
                self.emit(f"selp.f32 {d}, {v}, {d}, {p};")
            first = False

    def s_Init(self, s) -> None:
        self.comment(f"init {s.name} = {s.identity}")
        self.emit(f"mov.f32 {self.dest(s.name)}, {f32(s.identity)};")
        self.declared.add(s.name)

    def s_Accum(self, s) -> None:
        self.comment(f"{s.name} <- {s.op.name}({s.base or s.name}, {s.value})")
        if s.name not in self.env:
            self.seed(s)
        acc = self.val(s.name)
        base = self.val(s.base) if s.base else acc
        self.elementwise(s.op.name, acc, [base, self.val(s.value)])

    def seed(self, a) -> None:
        if a.op.identity is None:
            raise Unsupported(f"accumulator op {a.op.name!r} has no identity")
        self.emit(f"mov.f32 {self.dest(a.name)}, {f32(a.op.identity)};   // {a.name} = identity")

    def accums(self, body):
        for s in body:
            t = type(s).__name__
            if t == "Accum":
                yield s
            for f in ("body", "else_body"):
                yield from self.accums(getattr(s, f, ()) or ())

    def s_Loop(self, s) -> None:
        self.loop(s.axis.name, "0", str(dim(s.axis.extent)), "1", s.body, s.unroll)

    def s_StridedLoop(self, s) -> None:
        end = self.expr(s.end)[0] if s.end is not None else str(dim(s.axis.extent))
        self.loop(s.axis.name, self.expr(s.start)[0], end, self.expr(s.step)[0], s.body, s.unroll)

    def loop(self, var, start, end, step, body, unroll) -> None:
        self.comment(f"for {var} in {start}..{end} step {step}")
        mine = []
        for a in self.accums(body):     # seed accumulators reduced over this axis
            if var in a.axes and a.name not in self.declared and a.name not in self.acc_owner:
                self.seed(a)
                self.acc_owner[a.name] = var
                mine.append(a.name)
        if unroll and all(map(is_imm, (start, end, step))):
            trips = range(int(start), int(end), int(step))
            if len(trips) * self.size(body) <= UNROLL_LIMIT:
                for v in trips:
                    self.bind(var, str(v), "r")
                    self.visit(body)
                for m in mine:
                    del self.acc_owner[m]
                return
        i, p = self.new("r"), self.new("p")
        top, done = self.label(f"{var}_top"), self.label(f"{var}_end")
        self.emit(f"mov.s32 {i}, {start};")
        self.lines.append(f"{top}:")
        self.emit(f"setp.ge.s32 {p}, {i}, {end};")
        self.emit(f"@{p} bra {done};")
        self.bind(var, i, "r")
        self.visit(body)
        self.emit(f"add.s32 {i}, {i}, {step};")
        self.emit(f"bra.uni {top};")
        self.lines.append(f"{done}:")
        for m in mine:
            del self.acc_owner[m]

    def size(self, body) -> int:
        n = 0
        for s in body:
            n += 1
            if type(s).__name__ in ("Loop", "StridedLoop"):
                n += self.size(s.body) * max(1, dim(s.axis.extent))
            elif type(s).__name__ == "Cond":
                n += self.size(s.body) + self.size(s.else_body or ())
        return n

    def s_Cond(self, s) -> None:
        self.comment(f"if {fmt(s.cond)}")
        p = self.pred(s.cond)
        if p in ("0", "1"):
            self.visit(s.body if p == "1" else (s.else_body or ()))
            return
        other, done = self.label("else"), self.label("endif")
        self.emit(f"@!{p} bra {other if s.else_body else done};")
        self.visit(s.body)
        if s.else_body:
            self.emit(f"bra.uni {done};")
            self.lines.append(f"{other}:")
            self.visit(s.else_body)
        self.lines.append(f"{done}:")

    def s_Sync(self, s) -> None:
        if s.warp:
            self.emit("bar.warp.sync -1;")
        elif s.count:
            self.emit(f"bar.sync {s.barrier_id}, {s.count};")
        else:
            self.emit(f"bar.sync {s.barrier_id};")

    def s_Smem(self, s) -> None:
        self.comment(f"shared {s.dtype} {s.name}{list(s.extents)} (declared at module scope)")

    def s_WarpShuffle(self, s) -> None:
        self.comment(f"WarpShuffle({', '.join(s.state)}, length={s.length})")
        # A guarded tail exits whole shuffle groups (N is a multiple of `length`), so every live
        # lane's xor partners are live too; activemask names exactly them (0xffffffff would
        # name exited lanes, which is undefined). A group straddling the tail is refused.
        if self.tile_cells % s.length:
            raise Unsupported(f"WarpShuffle(length={s.length}) straddles the N={self.tile_cells} tail")
        mask = self.new("r")
        self.emit(f"activemask.b32 {mask};")
        off = s.length // 2
        while off:
            for st, sb in zip(s.state, s.state_b):
                d = self.dest(sb)
                self.emit(f"shfl.sync.bfly.b32 {d}, {self.val(st)}, {off}, 0x1f, {mask};")
            for a in s.combine_states:
                self.s_Assign(a, comment=False)
            off //= 2

    def s_TreeHalve(self, s) -> None:
        if s.inner is not None:
            raise Unsupported("TreeHalve with inner")
        self.comment(f"TreeHalve({', '.join(s.state)}, length={s.length}, tid={s.tid_var})")
        tid = self.val(s.tid_var)
        sync = f"bar.sync {s.barrier_id}" + (f", {s.barrier_count}" if s.barrier_count else "") + ";"
        half = s.length // 2
        while half:
            p, skip = self.new("p"), self.label("tree_skip")
            self.emit(f"setp.ge.s32 {p}, {tid}, {half};")
            self.emit(f"@{p} bra {skip};")
            other, _ = self.iop("+", tid, str(half))
            for buf, st, sb in zip(s.bufs, s.state, s.state_b):
                b, d = self.address(buf, tid)
                self.emit(f"ld.shared.f32 {self.dest(st)}, {self.at(b, d)};")
                b, d = self.address(buf, other)
                self.emit(f"ld.shared.f32 {self.dest(sb)}, {self.at(b, d)};")
            for a in s.combine_states:
                self.s_Assign(a, comment=False)
            for buf, st in zip(s.bufs, s.state):
                b, d = self.address(buf, tid)
                self.emit(f"st.shared.f32 {self.at(b, d)}, {self.val(st)};")
            self.lines.append(f"{skip}:")
            self.emit(sync)
            half //= 2
        for buf, st in zip(s.bufs, s.state):      # broadcast the root to every thread
            b, d = self.address(buf, "0")
            self.emit(f"ld.shared.f32 {self.dest(st)}, {self.at(b, d)};")

    def s_CpAsyncCopy(self, s) -> None:
        if s.swizzle != "NONE":
            raise Unsupported("swizzled cp.async")
        self.comment(f"cp.async[{s.nbytes}B] {s.smem}{idx(s.smem_index)} <- {s.src}{idx(s.src_index)}")
        shape = self.bufs[s.smem]["shape"]
        off = self.offset(s.smem_index, shape)
        if s.lane_index:
            off, _ = self.iop("+", off, self.offset(s.lane_index, shape))
        sb, sd = self.address(s.smem, off)
        gb, gd = self.address(s.src, self.offset(s.src_index, self.bufs[s.src]["shape"]))
        cache = "cg" if s.nbytes == 16 else "ca"
        self.emit(f"cp.async.{cache}.shared.global {self.at(sb, sd)}, {self.at(gb, gd)}, {s.nbytes};")

    def s_CpAsyncCommit(self, s) -> None:
        self.emit("cp.async.commit_group;")

    def s_CpAsyncWait(self, s) -> None:
        self.emit(f"cp.async.wait_group {s.group};")

    # ---- whole kernel ----------------------------------------------------------
    def prescan(self, body) -> None:
        for s in body:
            t = type(s).__name__
            if t == "Smem":
                if s.dtype not in SMEM_BYTES:
                    raise Unsupported(f"shared array of {s.dtype}")
                eb = SMEM_BYTES[s.dtype]
                self.smem.append((s.name, math.prod(s.extents) * eb, max(s.align, eb)))
                self.bufs[s.name] = dict(space="shared", shape=tuple(s.extents), bytes=eb)
            elif t == "Write":
                self.written.add(s.output)
            for f in ("body", "else_body"):
                self.prescan(getattr(s, f, ()) or ())

    def build(self) -> str:
        name = self.op.name
        self.prescan(self.op.body)
        pool = sum(b for _, b, _ in self.smem) > STATIC_SMEM_LIMIT
        off = 0
        for nm, nbytes, align in self.smem:
            off = -(-off // align) * align
            self.bufs[nm].update(sym="_smem_pool" if pool else nm, pool_off=off if pool else 0)
            off += nbytes

        params, prologue = [], []
        for a in self.karg:
            if a.get("scalar") or a["dtype"] != "f32":
                raise Unsupported(f"argument {a['name']} ({a['dtype']})")
            p, g = self.new("rd"), self.new("rd")
            params.append(f"\t.param .u64 p_{a['name']}")
            prologue += [f"\tld.param.u64 {p}, [p_{a['name']}];", f"\tcvta.to.global.u64 {g}, {p};"]
            self.bufs[a["name"]] = dict(space="global", base=g, shape=tuple(a["shape"]), bytes=4)
        self.tid, self.ntid, self.ctaid = self.new("r"), self.new("r"), self.new("r")
        lane, warp = self.new("r"), self.new("r")
        prologue += [f"\tmov.u32 {self.tid}, %tid.x;", f"\tmov.u32 {self.ntid}, %ntid.x;",
                     f"\tmov.u32 {self.ctaid}, %ctaid.x;",
                     f"\tand.b32 {lane}, {self.tid}, 31;", f"\tshr.u32 {warp}, {self.tid}, 5;"]
        for nm, _, _ in self.smem:
            b = self.bufs[nm]
            b["reg"] = r = self.new("r")
            prologue.append(f"\tmov.u32 {r}, {b['sym']};")
            if b["pool_off"]:
                prologue.append(f"\tadd.s32 {r}, {r}, {b['pool_off']};")
        self.bind("lane", lane, "r")
        self.bind("warp", warp, "r")
        self.bind("tid", self.tid, "r")

        self.visit(self.op.body)

        out = [f"// Generated by compile.py: Emmy Kernel IR -> PTX ({name})",
               f".version {PTX_VERSION}", f".target {TARGET}", ".address_size 64", ""]
        if pool:
            out.append(".extern .shared .align 16 .b8 _smem_pool[];")
        else:
            out += [f".shared .align {al} .b8 {nm}[{nb}];" for nm, nb, al in self.smem]
        blk = self.launch["block"]
        out += ["", f".visible .entry {name}(", ",\n".join(params), f")",
                f".maxntid {blk[0]}, {blk[1]}, {blk[2]}", "{"]
        decl = {"p": ".pred", "r": ".b32", "rd": ".b64", "f": ".f32"}
        out += [f"\t.reg {decl[k]} %{k}<{c + 1}>;" for k, c in self.n.items() if c]
        out += prologue + self.lines + ["\tret;", "}", ""]
        return "\n".join(out)


def load(ir_path: Path):
    g = Graph.from_dict(json.loads(ir_path.read_text()))
    kops = [n.op for n in g.nodes.values() if type(n.op).__name__ == "KernelOp"]
    if len(kops) != 1:
        raise Unsupported(f"expected one KernelOp, found {len(kops)}")
    op = kops[0]
    meta_path = ir_path.parent / "meta.json"
    if not meta_path.exists():
        raise Unsupported(f"no meta.json next to {ir_path}")
    meta = json.loads(meta_path.read_text())
    k = next((k for k in meta["kernels"] if k["entry"] == op.name), None)
    if k is None:
        raise Unsupported(f"meta.json has no kernel {op.name!r}")
    by_name = {a["name"]: a for a in k["args"]}
    return op, [by_name[n] for n in k["arg_order"]], k


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python compile.py path/to/kernel.ir.json > out.ptx", file=sys.stderr)
        return 2
    try:
        op, args, launch = load(Path(sys.argv[1]))
        ptx = Kernel(op, args, launch).build()
    except Unsupported as e:
        print(f"compile.py: unsupported: {e}", file=sys.stderr)
        return 1
    sys.stdout.write(ptx)
    return 0


if __name__ == "__main__":
    sys.exit(main())
