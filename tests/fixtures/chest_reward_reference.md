# Ordinary chest reward reference

The fixed V2.3.4 desktop-1.0.jar SHA-256 is
`cfad868ac8d65a88e71a0bf096fb09f78811e553effe0787c5309a655e081673`.

ChestRewardReference.java calls original AbstractDungeon.getRandomChest and
the selected original chest constructor. The constructor executes
AbstractChest.randomizeReward. The prepared ordinary chest size thresholds
are 50 and 33, matching Acts 1–3. An allocated room records the gold and relic
tier passed to the reward list. Relic inventory is empty. Audio and the
reward-screen transition use the recording boundaries from the earlier
reward probability harness.

The gzip fixture contains 300 grid rows and 72 seeded rows. The grid supplies
a size roll and every possible reward roll per size. The seeded rows use
seeds 0–35, each with a construction-only control and a construction-plus-open
trace. Both checkpoints store the original treasure RNG counter and raw state.
Opened rows record the requested relic tier and the optional sampled gold
amount. Python delegates tier selection to the production relic pool.

Compile RewardReference.java, ContentPoolReference.java,
RewardProbabilityReference.java and ChestRewardReference.java with JDK17 and
the fixed JAR on the classpath. Run ChestRewardReference with an output JSON
path in a temporary working directory. Compress JSON with gzip mtime zero.
The component scope covers ordinary base rewards and excludes the original
full game, inventory receipt and relic chest callbacks.
