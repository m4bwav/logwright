# Roblox (Luau, server Script)

Prints events as JSON lines to the output, which Studio and `LogService:GetLogHistory()` capture. No HTTP requests, no DataStore.

```lua
local HttpService = game:GetService("HttpService") -- JSONEncode and GUID only, no requests
local Telemetry = {}
local sid = HttpService:GenerateGUID(false):sub(1, 12)
function Telemetry.log(ev, f)
	print("TELEMETRY " .. HttpService:JSONEncode({
		ts = DateTime.now():ToIsoDate(), sid = sid, ev = ev, f = f or {},
	}))
end
game:GetService("ScriptContext").Error:Connect(function(msg, trace)
	Telemetry.log("error", { msg = msg, where = trace:match("[^\n]+") })
end)
return Telemetry
```

Never log `player.Name` or `UserId`; use a per-session index. Collect: copy the Output or dump `GetLogHistory()`, keep lines starting `TELEMETRY `, strip the prefix into a `.jsonl`. Roblox AnalyticsService (custom, funnel and economy events) is the hosted route; it sends data to Roblox and is the owner's call.
