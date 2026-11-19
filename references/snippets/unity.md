# Unity (C#)

Writes JSONL to `Application.persistentDataPath/telemetry/<sid>.jsonl`. Opt-in flag in PlayerPrefs. No network code.

```csharp
using System; using System.IO; using UnityEngine;
public static class Telemetry {
    static readonly string sid = Guid.NewGuid().ToString("N").Substring(0, 12);
    static string path;
    public static bool Enabled => PlayerPrefs.GetInt("telemetry_opt_in", 0) == 1;
    static string Q(string s) => "\"" + (s ?? "").Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", " ") + "\"";
    public static void Log(string ev, string fieldsJson = "{}") {
        if (!Enabled) return;
        if (path == null) {
            var dir = Path.Combine(Application.persistentDataPath, "telemetry");
            Directory.CreateDirectory(dir);
            path = Path.Combine(dir, sid + ".jsonl");
            Application.logMessageReceived += (msg, stack, type) => {
                if (type == LogType.Exception) Log("error", "{\"msg\":" + Q(msg) + "}");
            };
        }
        var scene = UnityEngine.SceneManagement.SceneManager.GetActiveScene().name;
        File.AppendAllText(path, "{\"ts\":" + Q(DateTime.UtcNow.ToString("o")) + ",\"sid\":" + Q(sid) +
            ",\"build\":" + Q(Application.version) + ",\"scene\":" + Q(scene) +
            ",\"ev\":" + Q(ev) + ",\"f\":" + fieldsJson + "}\n");
    }
}
```

Call `Telemetry.Log("level.fail", "{\"level\":\"2\",\"t\":41.5}")`. Player.log already holds exceptions; `lgw.py query` on the folder reads both.
