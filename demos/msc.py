import tsim
import time

c = tsim.Circuit.from_file("../circuits/msc_3.stim")


# Compilation step, takes about 3s
sampler = c.compile_detector_sampler(strategy="cutting")

start_time = time.perf_counter()
n = 10_000  # On GPU, increase batch size to fully utilize VRAM
sampler.sample(shots=n, batch_size=n)
end_time = time.perf_counter()
print(f"Time per shot: {(end_time - start_time) / n * 1e6:.2f} microseconds")

# %%
c = tsim.Circuit.from_file("../circuits/msd_5.stim")
sampler = c.compile_detector_sampler(strategy="cat5")  # Fastest with default strategy (cat5)
print(sampler)
samples = sampler.sample(shots=100_000, batch_size=100_000)


#%%
for d in [5, 7, 9]:
    c = tsim.Circuit.from_file(f"../circuits/star_d{d}.stim")
    sampler = c.compile_detector_sampler(strategy="cat5")  # Fastest with default strategy (cat5)
    print(sampler)
    samples = sampler.sample(shots=1_000, batch_size=1_000)
