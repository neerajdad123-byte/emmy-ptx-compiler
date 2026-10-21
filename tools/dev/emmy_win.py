"""Run the emmy CLI on Windows: puts the fcntl stand-in on sys.path first."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "winshim"))
from emmy.emmy import main
sys.exit(main())
