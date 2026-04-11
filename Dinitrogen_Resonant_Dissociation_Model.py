import numpy as np
import matplotlib.pyplot as plt

# Physical Constants (Locked to Manuscript Specifications)
amu = 1.66053906660e-27
m = 14.007 * amu
De = 1.57e-18   # Bond depth (~945 kJ/mol)
re = 1.1e-10    # Equilibrium distance (m)
a = 2.73e10     # Morse parameter
dt = 1e-17      # Timestep (10 as)
freq = 7.07e13  # 70.7 THz
omega = 2 * np.pi * freq
F0 = 23e-9      # 23 nN Force
Na = 6.022e23   # Avogadro's number
chirp_rate = -4.73e24  # Hz/s 

def get_morse_force(r_val):
    exp_term = np.exp(-a * (r_val - re))
    return -2 * De * a * (1 - exp_term) * exp_term

# Simulation State
r, v = re, 0.0
total_net_work = 0.0
step = 0

# Buffers for Plotting
times, positions, net_work_history = [], [], []

# Run until Dissociation (3x equilibrium)
while r < (3 * re):
    t = step * dt
    
    # --- CHIRPED PULSE FORCE ---
    # Phase calculation for linear chirp: phi = 2*pi * (f0*t + 0.5*beta*t^2)
    phase = 2 * np.pi * (freq * t + 0.5 * chirp_rate * t**2)
    ext_force = F0 * np.cos(phase)
    
    # Work calculation
    dW = ext_force * v * dt
    total_net_work += dW
    
    # Logging
    times.append(t * 1e15)
    positions.append(r * 1e10)
    net_work_history.append((total_net_work * Na) / 1000)
    
    # Velocity Verlet Integration
    f_int = get_morse_force(r)
    total_f = f_int + ext_force
    r_new = r + v * dt + (0.5 * total_f / m) * (dt**2)
    
    # --- NEXT FORCE CALCULATION (Chirped) ---
    next_t = t + dt
    next_phase = 2 * np.pi * (freq * next_t + 0.5 * chirp_rate * next_t**2)
    ext_force_next = F0 * np.cos(next_phase)
    
    f_int_next = get_morse_force(r_new)
    total_f_next = f_int_next + ext_force_next
    v = v + 0.5 * (total_f + total_f_next) / m * dt
    r = r_new
    step += 1

# --- REPORTING BLOCK ---
print(f"--- Manuscript Results (Chirped Pulse) ---")
print(f"Dissociation Time: {step * dt * 1e15:.2f} fs")
print(f"Net Work (Absorbed): {(total_net_work * Na) / 1000:.2f} kJ/mol")
print(f"Theoretical Bond Energy: {(De * Na) / 1000:.2f} kJ/mol")

# --- PLOTTING BLOCK ---
plt.figure(figsize=(10, 7))

# Top Plot: Bond Length
plt.subplot(2, 1, 1)
plt.plot(times, positions, color='blue', label='Bond Length')
plt.axhline(y=3*re*1e10, color='red', linestyle='--', label='Dissociation Threshold')
plt.ylabel('Bond Length (Ã…)')
plt.title('Resonant Vibration to Dissociation')
plt.legend()

# Bottom Plot: Energy Accumulation
plt.subplot(2, 1, 2)
plt.plot(times, net_work_history, color='green', label='Net Energy Absorbed')
plt.axhline(y=(De * Na / 1000), color='purple', linestyle='--', label='Bond Energy ($D_e$)')
plt.xlabel('Time (fs)')
plt.ylabel('Energy (kJ/mol)')
plt.legend()

plt.tight_layout()
plt.savefig('dissociation_analysis.png')