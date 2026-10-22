
import pytest

from nuclear_sim.nuclear.inventory import Isotope, IsotopeInventory


def make_chain():
    inventory = IsotopeInventory()

    inventory.add_isotope(
        Isotope("A", 10.0, 1.0, "B"),
        initial_atoms=1000.0,
    )
    inventory.add_isotope(
        Isotope("B", 20.0, 0.5, "C"),
        initial_atoms=0.0,
    )
    inventory.add_isotope(
        Isotope("C", None),
        initial_atoms=0.0,
    )

    return inventory


def test_parent_halves_after_one_half_life():
    state = make_chain().simulate(10.0)

    assert state.atoms["A"] == pytest.approx(500.0)


def test_daughter_is_produced():
    state = make_chain().simulate(10.0)

    assert state.atoms["B"] > 0.0


def test_stable_isotope_does_not_decay():
    inventory = IsotopeInventory()
    inventory.add_isotope(
        Isotope("Stable", None),
        initial_atoms=500.0,
    )

    state = inventory.simulate(1000.0)

    assert state.atoms["Stable"] == pytest.approx(500.0)
    assert state.activities_bq["Stable"] == 0.0


def test_total_number_of_atoms_is_conserved():
    state = make_chain().simulate(100.0)

    assert sum(state.atoms.values()) == pytest.approx(1000.0)


def test_unknown_daughter_is_rejected():
    inventory = IsotopeInventory()
    inventory.add_isotope(
        Isotope("A", 10.0, 1.0, "Missing"),
        initial_atoms=100.0,
    )

    with pytest.raises(ValueError):
        inventory.simulate(10.0)


def test_negative_time_is_rejected():
    with pytest.raises(ValueError):
        make_chain().simulate(-1.0)
