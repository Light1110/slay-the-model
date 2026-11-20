# Advanced opening menu reference

NeowMenuProtocolReference.java runs the four original reward constructors
against the fixed V2.3.4 JAR with prepared player health and placeholder
localization. It records reward and drawback enum identifiers, integer bounds,
results and RNG state. The fixture includes 25 controlled cases covering all
legal benefit indices per drawback and every index in the first two slots.
The 49 seeded cases cover seeds −1 through 47. They also record the next
0.33 probability draw from the same reference RNG.

Project regressions exercise the opening room menu for all four roles at A0
and A20 for the seeded vectors. For the three-card choice, the project also
executes the existing reward action and checks its first rarity draw.
Original UI and reward execution are outside the reference component.

To reproduce, compile RewardReference.java, ContentPoolReference.java and
NeowMenuProtocolReference.java with JDK17 against the fixed desktop-1.0.jar.
The JAR SHA-256 is
`cfad868ac8d65a88e71a0bf096fb09f78811e553effe0787c5309a655e081673`.
Run NeowMenuProtocolReference with an output JSON path in a temporary working
directory, then gzip the JSON with mtime zero.
