import os

def main():
    # 1. Inject Preference into Tabs Settings XML
    pref_tag = '\n    <ListPreference android:key="tab_switcher_type" android:title="Tab switcher" android:summary="%s" android:defaultValue="1" />\n'
    for root, dirs, files in os.walk("chrome"):
        for f in files:
            if f in ["tabs_settings_preferences.xml", "tab_management_preferences.xml", "tabs_preferences.xml"]:
                p = os.path.join(root, f)
                with open(p, "r", encoding="utf-8") as xf:
                    c = xf.read()
                if "tab_switcher_type" not in c:
                    c = c.replace("</PreferenceScreen>", pref_tag + "</PreferenceScreen>")
                    with open(p, "w", encoding="utf-8") as xf:
                        xf.write(c)

    # 2. Hook Java Settings fragment to populate entries directly
    pop_code = """
        androidx.preference.ListPreference tabPref = findPreference("tab_switcher_type");
        if (tabPref != null) {
            CharSequence[] entries = new CharSequence[]{"Default", "Original (Vertical)", "Horizontal", "Grid", "List"};
            CharSequence[] values = new CharSequence[]{"0", "1", "2", "3", "4"};
            tabPref.setEntries(entries);
            tabPref.setEntryValues(values);
        }
    """
    for root, dirs, files in os.walk("chrome/android"):
        for f in files:
            if f in ["TabsSettings.java", "TabManagementSettings.java", "MainSettings.java"]:
                jp = os.path.join(root, f)
                try:
                    with open(jp, "r", encoding="utf-8", errors="ignore") as jf:
                        jc = jf.read()
                except Exception:
                    continue
                if "onCreatePreferences" in jc and "tab_switcher_type" not in jc:
                    idx = jc.find("super.onCreatePreferences(")
                    if idx != -1:
                        end_idx = jc.find(";", idx) + 1
                        jc = jc[:end_idx] + pop_code + jc[end_idx:]
                        with open(jp, "w", encoding="utf-8") as jf:
                            jf.write(jc)

    # 3. Hook Tab Switcher Logic in Java
    hook = """public static boolean isGridTabSwitcherEnabled(Context context) {
            try {
                android.content.SharedPreferences sp = android.preference.PreferenceManager.getDefaultSharedPreferences(context);
                String mode = sp.getString("tab_switcher_type", "1");
                if ("1".equals(mode) || "4".equals(mode)) return false;
            } catch (Exception ignored) {}
    """
    for root, dirs, files in os.walk("chrome"):
        for f in files:
            if f.endswith(".java"):
                jp = os.path.join(root, f)
                try:
                    with open(jp, "r", encoding="utf-8", errors="ignore") as f:
                        jc = f.read()
                except Exception:
                    continue
                if "isGridTabSwitcherEnabled" in jc and "Context context" in jc:
                    jc = jc.replace("public static boolean isGridTabSwitcherEnabled(Context context) {", hook)
                    with open(jp, "w", encoding="utf-8") as f:
                        f.write(jc)

if __name__ == "__main__":
    main()
