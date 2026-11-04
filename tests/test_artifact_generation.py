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

    # Check PCB single unified zone geometry (140mm x 95mm)
    pcb_content = (output_dir / "wilo_receiver.kicad_pcb").read_text(encoding="utf-8")
    assert '(start 50.0 50.0) (end 190.0 50.0)' in pcb_content, "Missing 140mm top edge"
    assert '(start 190.0 145.0) (end 50.0 145.0)' in pcb_content, "Missing 95mm bottom edge"
    assert "gr_rect" not in pcb_content, "Milled isolation slots should be removed in single-zone design"
    assert "MAIN SYSTEM POWER: 5V DC USB-C ONLY" in pcb_content

    # Check schematic modular structure
    sch_content = (output_dir / "wilo_receiver.kicad_sch").read_text(encoding="utf-8")
    assert 'rev "3.0"' in sch_content
    assert "1. RASPBERRY PI ZERO 2W INTERFACE" in sch_content
    assert "7. DUAL POWER RELAYS" in sch_content
