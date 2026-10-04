package com.evolyrics;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import net.minecraftforge.fml.loading.FMLPaths;

import java.io.IOException;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

public final class Settings {
    public static final String[] POSITIONS = {"Around", "Center", "Top", "Bottom"};
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    public static Settings I = new Settings();

    public boolean enabled = true;
    public boolean island = true;
    public float size = 1.0f;
    public float distance = 9.0f;
    public float scatter = 0.7f;
    public float opacity = 1.0f;
    public float glow = 0.9f;
    public float blur = 0.4f;
    public float syncOffset = 0f;
    public String inEffect = "RISE";
    public String outEffect = "FADE";
    public int position = 0;
    public boolean throughWalls = true;
    public boolean useBridge = false;
    public String lastSong = "";

    public LyricEffect in() {
        LyricEffect e = LyricEffect.parse(inEffect);
        return e == null ? LyricEffect.RISE : e;
    }

    public LyricEffect out() {
        LyricEffect e = LyricEffect.parse(outEffect);
        return e == null ? LyricEffect.FADE : e;
    }

    private static Path file() {
        return FMLPaths.CONFIGDIR.get().resolve("evolyrics").resolve("settings.json");
    }

    public static void load() {
        try {
            Path f = file();
            if (Files.isRegularFile(f)) {
                try (Reader r = Files.newBufferedReader(f, StandardCharsets.UTF_8)) {
                    Settings s = GSON.fromJson(r, Settings.class);
                    if (s != null) I = s;
                }
            }
        } catch (Exception ignored) {
        }
    }

    public static void save() {
        try {
            Path f = file();
            Files.createDirectories(f.getParent());
            Files.writeString(f, GSON.toJson(I), StandardCharsets.UTF_8);
        } catch (IOException ignored) {
        }
    }
}
