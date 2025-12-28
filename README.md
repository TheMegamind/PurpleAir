<table>
<tr>
<td width="100">
<img src="https://github.com/TheMegamind/PurpleAir/blob/main/assets/PurpleAir.png"
     width="100" alt="PurpleAir Logo">
</td>
<td>

# PurpleAir Plus – A Custom Integration for Home Assistant

</td>
</tr>
</table>

#### Hyper-local air quality monitoring using nearby PurpleAir sensors, with configurable averaging, conversion formulas, and live polling control.

---

## 🌫 Why Use PurpleAir?

PurpleAir sensors provide **hyper-local, real-time air quality data**, which can provide a more representative picture of the air quality where you live.

This is especially useful when:

* Official air quality monitors are **miles away**
* **Wildfire smoke** affects neighborhoods unevenly
* Terrain, inversions, or weather create **micro-climates**

---

> **⚠️ Important disclaimer**  
> Home Assistant typically does not permit built-in integrations to provide entities based on data not directly provided by the underlying API, prefering to leave the interpretation of said data to the user. This custom integration performs **additional calculations and interpretations** (conversions, sensor averaging, categories, etc.), that are subject to change and **not provided directly by the PurpleAir API**. Use caution if you are relying on this data this data responsibly, as the software is provided "as is," with no liability from the author.

---

## ✨ Custom Integration Features

### Core Capabilities

* Automatically discovers **public PurpleAir sensors** near a given location
* **Multi-sensor averaging** of nearby monitors for improved stability and reliability
* Optional **weighted averaging** (distance + sensor reliability)
* Optional use of **private sensors** via sensor index + read key
* Fully async, coordinator-based architecture

---

## 🔢 PM₂.₅ Conversion Formulas

This integration supports multiple conversion methods used by air-quality agencies and research groups:

| Conversion | Best For | Notes |
|-----------|---------|-------|
| **US EPA** | Most users | Recommended default |
| **Woodsmoke** | Wildfire regions | Better smoke accuracy |
| **AQ&U** | Mountain / inversion zones | Utah DEQ |
| **LRAPA** | Humid climates | Oregon LRAPA |
| **CF = 1** | Indoor sensors | Raw factory value |
| **None** | Research | No correction |

> **Recommendation:**  
> Use **US EPA** unless you are specifically tuning for wildfire smoke.

---

## 📦 Installation (HACS – Custom Repository)

> *This integration is currently in beta and not listed in the HACS store.*

1. Open **HACS → Integrations → Custom repositories**
2. Add this url:

   ```
   https://github.com/TheMegamind/PurpleAir
   ```

3. Category: **Integration**
4. Install → Restart Home Assistant
5. Go to **Settings → Devices & Services → Add Integration**
6. Select **PurpleAir**

---

## ⚙️ Configuration

### Initial Setup

| Setting | Description |
|-------|-------------|
| **API Key** | PurpleAir API key |
| **Device Search** | Auto-discover nearby sensors |
| **Latitude / Longitude** | Center point for search |
| **Search Range** | Radius (0.1–50 miles/km) |
| **Unit** | Miles or kilometers |
| **Weighted** | Enable weighted averaging |
| **Conversion** | PM₂.₅ conversion formula |
| **Update Interval** | Polling interval (minutes) |

If **Device Search** is disabled, you may provide:

* **Sensor Index** (single sensor ID)
* **Read Key** (private sensors only)

### Options (after setup)

Editable at any time:

* Search range
* Miles / kilometers
* Weighted averaging
* Conversion method
* Update interval

> Latitude and longitude are fixed after setup.  
> To change location, remove and re-add the integration.

---

## 📊 Entities Provided

### Sensors

| Entity | Description |
|------|-------------|
| **AQI** | Calculated AQI value |
| **AQI Delta** | Change since previous poll |
| **AQI Level** | Numeric level (1–6) |
| **AQI Color** | Green / Yellow / Orange / Red / Purple / Maroon |
| **Category** | AQI category (Good, Moderate, etc.) |
| **Health Advisory** | Long advisory text |
| **Health Status** | `online` / `offline` |
| **Sites** | Sensors contributing to the average |
| **Conversion** | Active conversion method |

### Control

| Entity | Description |
|------|-------------|
| **Update Interval** | Live polling interval control (minutes) |

> The **Update Interval** control appears directly on the **device page** and takes effect immediately.

---

## ⏱ Update Interval Behavior

| Interval | Effect |
|--------|-------|
| **1–5 min** | Rapid response, higher API usage |
| **10–15 min** | Recommended balance |
| **30–60 min** | Lowest API usage |

**Notes:**
* Shorter intervals improve responsiveness, **not accuracy**
* Wildfire monitoring may benefit from faster polling
* Interval changes apply immediately without restart

---

## 🛠 Troubleshooting

* **AQI is `unknown`** → Check API key
* **No sensors found** → Increase search range
* **Private sensor not working** → Verify read key

---

## 📄 License

MIT License — see `LICENSE`.

---

## ⚠️ Trademarks & Disclaimers

* **PurpleAir®** name and logo are trademarks of **PurpleAir, Inc.**
* **Home Assistant®** name and logo are trademarks of **Nabu Casa, Inc.**
* This project is **independent**, community-maintained, and **not affiliated with or endorsed by PurpleAir or Nabu Casa**.


