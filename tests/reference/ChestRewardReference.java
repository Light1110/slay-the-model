// Original ordinary-chest construction and opening with recorded rewards.
import com.google.gson.*;
import com.megacrit.cardcrawl.core.*;
import com.megacrit.cardcrawl.dungeons.AbstractDungeon;
import com.megacrit.cardcrawl.relics.AbstractRelic;
import com.megacrit.cardcrawl.rewards.chests.AbstractChest;
import com.megacrit.cardcrawl.ui.buttons.ProceedButton;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

public class ChestRewardReference {
    public static class Room extends RewardProbabilityReference.RecordingRoom {
        Integer gold;
        String tier;

        public void addGoldToRewards(int amount) { gold = amount; }
        public void addRelicToRewards(AbstractRelic.RelicTier rarity) { tier = rarity.name(); }
    }

    static class FixedRolls extends RewardProbabilityReference.Trace {
        final Iterator<Integer> rolls;
        FixedRolls(int size, int reward) {
            super(0);
            rolls = Arrays.asList(size, reward).iterator();
        }

        public int random(int start, int end) {
            if (start != 0 || end != 99) throw new AssertionError("Unexpected bounds");
            int value = rolls.next();
            calls.add(Arrays.asList("int_range", start, end, value));
            return value;
        }
    }

    static Map<String, Object> observe(RewardProbabilityReference.Trace rng, Room room,
                                       boolean open, boolean seeded) {
        room.gold = null;
        room.tier = null;
        AbstractDungeon.treasureRng = rng;
        AbstractChest chest = AbstractDungeon.getRandomChest();
        Map<String, Object> row = new LinkedHashMap<>();
        row.put("size", chest.getClass().getSimpleName().replace("Chest", "").toLowerCase(Locale.ROOT));
        row.put("base_gold", chest.goldReward ? chest.GOLD_AMT : 0);
        row.put("tier", chest.relicReward.name().replace("_RELIC", ""));
        row.put("entry_calls", new ArrayList<>(rng.calls));
        if (seeded) row.put("entry_state", RewardReference.state(rng));
        if (open) chest.open(false);
        row.put("gold", room.gold);
        row.put("opened_tier", room.tier);
        row.put("calls", new ArrayList<>(rng.calls));
        if (seeded) row.put("final_state", RewardReference.state(rng));
        return row;
    }

    public static void main(String[] args) throws Exception {
        ContentPoolReference.setup(new JsonArray());
        Settings.isDailyRun = false;
        Settings.isFinalActAvailable = false;
        CardCrawlGame.sound = (RewardProbabilityReference.SilentSound)
            RewardReference.u.allocateInstance(RewardProbabilityReference.SilentSound.class);
        AbstractDungeon.overlayMenu = (OverlayMenu) RewardReference.u.allocateInstance(OverlayMenu.class);
        AbstractDungeon.overlayMenu.proceedButton = (ProceedButton) RewardReference.u.allocateInstance(ProceedButton.class);
        AbstractDungeon.combatRewardScreen = (RewardProbabilityReference.RecordingScreen)
            RewardReference.u.allocateInstance(RewardProbabilityReference.RecordingScreen.class);
        for (String name : new String[]{"smallChestChance", "mediumChestChance"}) {
            java.lang.reflect.Field field = AbstractDungeon.class.getDeclaredField(name);
            field.setAccessible(true);
            field.setInt(null, name.equals("smallChestChance") ? 50 : 33);
        }
        Room room = (Room) RewardReference.u.allocateInstance(Room.class);
        RewardProbabilityReference.room(room);
        List<Map<String, Object>> grid = new ArrayList<>();
        for (int size : new int[]{0, 50, 83}) {
            for (int reward = 0; reward < 100; reward++) {
                grid.add(observe(new FixedRolls(size, reward), room, false, false));
            }
        }
        List<Map<String, Object>> seeded = new ArrayList<>();
        for (long seed = 0; seed < 36; seed++) {
            for (boolean open : new boolean[]{false, true}) {
                Map<String, Object> row = observe(new RewardProbabilityReference.Trace(seed), room, open, true);
                row.put("seed", Long.toString(seed));
                row.put("open", open);
                seeded.add(row);
            }
        }
        Map<String, Object> output = new LinkedHashMap<>();
        output.put("grid", grid);
        output.put("seeded", seeded);
        Gson gson = new GsonBuilder().serializeNulls().create();
        Files.write(Paths.get(args[0]), gson.toJson(output).getBytes(StandardCharsets.UTF_8));
        System.out.println("Actual original chest rows: " + (grid.size() + seeded.size()));
    }
}
