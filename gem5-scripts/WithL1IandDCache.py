from m5.objects import *
import sys  # Import sys to access command-line arguments

class L1_ICache(Cache):
    size = '32kB'
    assoc = 8
    tag_latency = 20
    data_latency = 20
    response_latency = 20
    mshrs = 20
    tgts_per_mshr = 8

class L1_DCache(Cache):
    size = '32kB'
    assoc = 8
    tag_latency = 20
    data_latency = 20
    response_latency = 20
    mshrs = 20
    tgts_per_mshr = 8

# Ensure an argument is provided
if len(sys.argv) < 2:
    print("Usage: script.py <binary_path>")
    sys.exit(1)

binary = sys.argv[1]  # Take binary path from command-line argument

# Create the system
system = System()
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

# Configure the memory
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# Create the CPU
system.cpu = TimingSimpleCPU()

# Set up the memory bus
system.membus = SystemXBar()
system.cpu.icache = L1_ICache()
system.cpu.dcache = L1_DCache()

# Connect the CPU's cache ports to the memory bus
# Connect instruction cache ports
system.cpu.icache.cpu_side = system.cpu.icache_port
system.cpu.icache.mem_side = system.membus.cpu_side_ports

# Connect data cache ports
system.cpu.dcache.cpu_side = system.cpu.dcache_port
system.cpu.dcache.mem_side = system.membus.cpu_side_ports

# Create an interrupt controller and connect it to the memory bus
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# Connect the system's port to the memory bus
system.system_port = system.membus.cpu_side_ports

# Set up the memory controller and connect it to the memory bus
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# Set up the workload
system.workload = SEWorkload.init_compatible(binary)

process = Process()
process.cmd = [binary]  # Set the command to run the binary
system.cpu.workload = process  # Assign the workload to the CPU
system.cpu.createThreads()  # Create threads for the CPU

# Instantiate the system and begin execution
root = Root(full_system=False, system=system)
m5.instantiate()

print("Beginning simulation!")
exit_event = m5.simulate()

print('Exiting @ tick {} because {}'.format(m5.curTick(), exit_event.getCause()))
