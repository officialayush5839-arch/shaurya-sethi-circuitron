"""Tests for Wilo receiver PCB artifact generation."""
from pathlib import Path
import pytest


def test_receiver_artifacts_generated(tmp_path):
    """Verify that build_receiver_artifacts outputs all design files."""
    from scripts.generate_wilo_pcb import build_receiver_artifacts

    output_dir = tmp_path / "receiver_out"
    build_receiver_artifacts(output_dir=str(output_dir))

    assert (output_dir / "wilo_receiver.net").exists(), "KiCad netlist not generated"
    assert (output_dir / "wilo_receiver.sch").exists(), "KiCad schematic not generated"
    assert (output_dir / "wilo_receiver.kicad_pcb").exists(), "KiCad PCB layout not generated"
    assert (output_dir / "bom.csv").exists(), "Bill of Materials CSV not generated"

    # Check BOM contents
    bom_content = (output_dir / "bom.csv").read_text(encoding="utf-8")
    assert "J1" in bom_content
    assert "J_USBC" in bom_content
    assert "U_LORA" in bom_content
    assert "ACS712T-30A" in bom_content
    assert "MOV1" in bom_content
    assert "R_OPT1" in bom_content
    assert "R_LED2" in bom_content
    assert "C_ACS" in bom_content
