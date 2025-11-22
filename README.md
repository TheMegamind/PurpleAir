
---

# PurpleAir AQI – Home Assistant Integration

Fetches PM2.5-based AQI from nearby PurpleAir sensors, with averaging and PM2.5 conversion options.

---

## ✨ Features

* Automatically finds **public PurpleAir sensors** near a location
* Supports **PM2.5 conversion formulas**:

  * US EPA
  * Woodsmoke
  * AQ&U
  * LRAPA
  * CF=1
  * None
* Uses **averaged AQI** from multiple sensors
* Supports **weighted averaging** (distance + sensor quality)
* Adjustable:

  * Search radius
  * Miles/kilometers
  * Update interval
  * Use of weighted calculations
* Provides three sensor attributes:

  * **aqi** – PM2.5 AQI (converted)
  * **category** – Good / Moderate / Unhealthy, etc.
  * **sites** – List of sensors included in the calculation
* Compatible with **HACS** via Custom Repository
* Minimal configuration required
* Fully asynchronous and efficient

---

## 📦 Installation (HACS – Custom Repository)

1. Open **HACS → Integrations → Custom repositories**
2. Add this URL:

   ```
   https://github.com/TheMegamind/purple_air
   ```
3. Category: **Integration**
4. Install → Restart Home Assistant
5. Go to **Settings → Devices & Services → Add Integration**
6. Choose **PurpleAir AQI**

---

## ⚙️ Configuration

### Initial Setup Fields

| Setting                  | Description                                |
| ------------------------ | ------------------------------------------ |
| **API Key**              | PurpleAir API key (required)               |
| **Device Search**        | Whether to auto-locate nearby sensors      |
| **Latitude / Longitude** | Center coordinate for search box           |
| **Search Range**         | Radius around the coordinate (0.1–50)      |
| **Unit**                 | Miles or kilometers                        |
| **Weighted**             | Enable distance/quality weighted averaging |
| **Conversion**           | PM2.5 conversion method                    |
| **Update Interval**      | Minutes between sensor refresh             |

If *Device Search* is OFF, you may supply:

* **Sensor Index** (ID of a single PurpleAir sensor)
* **Read Key** (for private sensors only)

### Options (after setup)

Can be edited anytime:

* Search Range
* Unit (miles/km)
* Weighted
* Conversion method
* Update interval

Latitude and longitude remain fixed after initial setup.

---

## 🧪 Entity Provided

| Entity                 | Type   | Description                                |
| ---------------------- | ------ | ------------------------------------------ |
| `sensor.purpleair_aqi` | Sensor | PM2.5 AQI value, category, and sensor list |

---

## 🔧 Example Usage

Send AQI notifications through Pushover:

```yaml
service: notify.pushover
data:
  title: "Air Quality"
  message: >
    Current AQI: {{ states('sensor.purpleair_aqi') }} –
    {{ state_attr('sensor.purpleair_aqi', 'category') }}
```

---

## 🛠 Troubleshooting

* If AQI remains `unknown`, verify your **API key**.
* If no sensors are detected, increase **search_range** in Options.
* For private sensors, ensure **read_key** is correct.

---

## 📄 License

This project is licensed under the MIT License.
See the `LICENSE` file for details.

## Brand Disclaimer

The **PurpleAir** name and logo are trademarks of **PurpleAir, Inc.**  
This project is an independent, community-maintained integration for Home Assistant and is **not affiliated with, endorsed by, or sponsored by PurpleAir, Inc.** in any way.

---
