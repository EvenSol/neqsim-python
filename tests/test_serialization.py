"""Regression tests for portable, transactional NeqSim process archives."""

import jpype

from neqsim import jneqsim, open_neqsim, save_neqsim


def _build_recycle_process():
    fluid = jneqsim.thermo.system.SystemSrkEos(298.15, 50.0)
    fluid.addComponent("methane", 0.9)
    fluid.addComponent("ethane", 0.1)
    fluid.setMixingRule("classic")

    process = jneqsim.process.processmodel.ProcessSystem("xstream portability process")

    feed = jneqsim.process.equipment.stream.Stream("feed", fluid)
    feed.setFlowRate(50000.0, "kg/hr")
    feed.setTemperature(25.0, "C")
    feed.setPressure(50.0, "bara")
    process.add(feed)

    recycle_gas = jneqsim.process.equipment.stream.Stream("recycle gas", fluid.clone())
    recycle_gas.setFlowRate(5000.0, "kg/hr")
    recycle_gas.setTemperature(25.0, "C")
    recycle_gas.setPressure(50.0, "bara")
    process.add(recycle_gas)

    mixer = jneqsim.process.equipment.mixer.Mixer("mixer")
    mixer.addStream(feed)
    mixer.addStream(recycle_gas)
    process.add(mixer)

    cooler = jneqsim.process.equipment.heatexchanger.Cooler(
        "cooler", mixer.getOutletStream()
    )
    cooler.setOutTemperature(15.0, "C")
    process.add(cooler)

    separator = jneqsim.process.equipment.separator.Separator(
        "20-VA-01", cooler.getOutletStream()
    )
    process.add(separator)

    splitter = jneqsim.process.equipment.splitter.Splitter(
        "splitter", separator.getGasOutStream()
    )
    splitter.setSplitFactors([0.9, 0.1])
    process.add(splitter)

    export_gas = jneqsim.process.equipment.stream.Stream(
        "export gas", splitter.getSplitStream(0)
    )
    process.add(export_gas)

    recycle = jneqsim.process.equipment.util.Recycle("recycle")
    recycle.addStream(splitter.getSplitStream(1))
    recycle.setOutletStream(recycle_gas)
    recycle.setTolerance(1e-4)
    process.add(recycle)

    process.run()
    return process


def test_recycle_process_round_trip_is_portable_on_java_17_plus(tmp_path):
    assert jpype.getJVMVersion()[0] >= 17

    management_factory = jpype.JClass("java.lang.management.ManagementFactory")
    jvm_arguments = [
        str(argument)
        for argument in management_factory.getRuntimeMXBean().getInputArguments()
    ]
    assert not any("java.base/java.util" in argument for argument in jvm_arguments)

    process = _build_recycle_process()
    assert process.solved() is True

    archive = tmp_path / "recycle-process.neqsim"
    assert save_neqsim(process, str(archive)) is True

    restored = open_neqsim(str(archive))
    assert restored is not None
    assert restored.getUnit("20-VA-01") is not None
    assert restored.getUnit("export gas") is not None

    restored.run()
    assert restored.solved() is True


def test_failed_save_does_not_publish_a_partial_archive(tmp_path):
    new_archive = tmp_path / "new.neqsim"
    assert save_neqsim(object(), str(new_archive)) is False
    assert new_archive.exists() is False
    assert list(tmp_path.iterdir()) == []

    archive = tmp_path / "existing.neqsim"
    java_string = jpype.JClass("java.lang.String")("previous valid archive")
    assert save_neqsim(java_string, str(archive)) is True
    original_contents = archive.read_bytes()

    assert save_neqsim(object(), str(archive)) is False
    assert archive.read_bytes() == original_contents
    assert list(tmp_path.iterdir()) == [archive]
    assert str(open_neqsim(str(archive))) == "previous valid archive"
