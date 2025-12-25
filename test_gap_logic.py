"""Quick test to verify gap logic"""

# Simulate the enumerate logic
reels = ['reel1', 'reel2', 'reel3', 'reel4', 'reel5', 'reel6']

print("Testing OLD logic (enumerate starting at 0):")
for reel_idx, reel in enumerate(reels):
    if reel_idx < len(reels):
        print(f"  Reel {reel_idx}: Would add gap? {reel_idx < len(reels)} (idx={reel_idx}, len={len(reels)})")

print("\nTesting NEW logic (enumerate starting at 1):")
for reel_idx, reel in enumerate(reels, 1):
    if reel_idx < len(reels):
        print(f"  Reel {reel_idx}: Would add gap? {reel_idx < len(reels)} (idx={reel_idx}, len={len(reels)})")
    else:
        print(f"  Reel {reel_idx}: NO GAP (last reel)")
