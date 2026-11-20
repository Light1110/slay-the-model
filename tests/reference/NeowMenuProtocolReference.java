// Execute the original reward constructors with prepared metadata.
import com.google.gson.Gson;
import com.megacrit.cardcrawl.dungeons.AbstractDungeon;
import com.megacrit.cardcrawl.localization.CharacterStrings;
import com.megacrit.cardcrawl.localization.LocalizedStrings;
import com.megacrit.cardcrawl.neow.NeowEvent;
import com.megacrit.cardcrawl.neow.NeowReward;
import java.lang.reflect.Field;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

public class NeowMenuProtocolReference {
    static final class Fixed extends ContentPoolReference.Trace {
        final Iterator<Integer> values;

        Fixed(List<Integer> values) {
            super(0);
            this.values = values.iterator();
        }

        public int random(int lo, int hi) {
            int value = values.next();
            if (value < lo || value > hi) throw new AssertionError("Invalid prepared roll");
            calls.add(Arrays.asList("int_range", lo, hi, value));
            return value;
        }
    }

    static Map<String, Object> menu(Field rngField, Field typeField, Field drawbackField,
                                    ContentPoolReference.Trace rng) throws Exception {
        rngField.set(null, rng);
        List<String> types = new ArrayList<>();
        String drawback = null;
        for (int category = 0; category < 4; category++) {
            NeowReward reward = new NeowReward(category);
            types.add(typeField.get(reward).toString());
            if (category == 2) drawback = drawbackField.get(reward).toString();
        }
        Map<String, Object> row = new LinkedHashMap<>();
        row.put("types", types);
        row.put("drawback", drawback);
        row.put("calls", new ArrayList<>(rng.calls));
        return row;
    }

    public static void main(String[] args) throws Exception {
        RewardReference.setup();
        Field characters = LocalizedStrings.class.getDeclaredField("characters");
        characters.setAccessible(true);
        CharacterStrings strings = new CharacterStrings();
        strings.NAMES = new String[]{"prepared"};
        strings.TEXT = new String[100];
        Arrays.fill(strings.TEXT, "prepared");
        strings.UNIQUE_REWARDS = strings.TEXT;
        characters.set(null, Map.of("Neow Reward", strings, "Neow Event", strings));
        AbstractDungeon.player.maxHealth = 80;
        AbstractDungeon.player.currentHealth = 80;
        Field rngField = NeowEvent.class.getDeclaredField("rng");
        Field typeField = NeowReward.class.getDeclaredField("type");
        Field drawbackField = NeowReward.class.getDeclaredField("drawback");
        for (Field field : new Field[]{rngField, typeField, drawbackField}) field.setAccessible(true);

        List<Object> grid = new ArrayList<>();
        int index = 0;
        for (int cost = 0; cost < 4; cost++) {
            int count = cost == 3 ? 7 : 6;
            for (int benefit = 0; benefit < count; benefit++, index++) {
                Fixed rng = new Fixed(Arrays.asList(index % 6, index % 5, cost, benefit, 0));
                grid.add(menu(rngField, typeField, drawbackField, rng));
            }
        }
        List<Object> seeded = new ArrayList<>();
        for (long seed = -1; seed < 48; seed++) {
            ContentPoolReference.Trace rng = new ContentPoolReference.Trace(seed);
            Map<String, Object> row = menu(rngField, typeField, drawbackField, rng);
            row.put("seed", Long.toString(seed));
            row.put("state", RewardReference.state(rng));
            row.put("next_card_rarity", rng.randomBoolean(0.33f));
            seeded.add(row);
        }
        Map<String, Object> output = new LinkedHashMap<>();
        output.put("grid", grid);
        output.put("seeded", seeded);
        Files.write(Paths.get(args[0]), new Gson().toJson(output).getBytes(StandardCharsets.UTF_8));
        System.out.println("Original menu constructor rows: " + (grid.size() + seeded.size()));
    }
}
