
```
sensor_receiver
├─ Dll
│  ├─ .idea
│  │  ├─ .name
│  │  ├─ Python-WitProtocol.iml
│  │  ├─ inspectionProfiles
│  │  │  ├─ Project_Default.xml
│  │  │  └─ profiles_settings.xml
│  │  ├─ misc.xml
│  │  └─ modules.xml
│  └─ lib
│     ├─ Modular
│     │  ├─ JY901.py
│     │  ├─ WT901C485.py
│     │  └─ interface
│     │     └─ i_operating_equipment.py
│     ├─ __pycache__
│     │  ├─ device_model.cpython-310.pyc
│     │  └─ device_model.cpython-39.pyc
│     ├─ data_processor
│     │  ├─ interface
│     │  │  └─ i_data_processor.py
│     │  └─ roles
│     │     └─ jy901s_dataProcessor.py
│     ├─ device_model.py
│     ├─ protocol_resolver
│     │  ├─ interface
│     │  │  └─ i_protocol_resolver.py
│     │  └─ roles
│     │     ├─ protocol_485_resolver.py
│     │     └─ wit_protocol_resolver.py
│     └─ utils
│        └─ byte_array_converter.py
├─ README.md
├─ bash
│  ├─ commcheck.sh
│  ├─ sensor_receiver_service
│  ├─ service_del.sh
│  ├─ service_reg.sh
│  └─ setup.sh
├─ dat
│  └─ config.json
└─ src
   ├─ calculator.py
   ├─ main.py
   ├─ rx.py
   └─ server.py

```