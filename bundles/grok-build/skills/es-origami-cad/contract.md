<!-- sha256: 9032a5ef61aeb8f817ebab59754efa00ee433cda53d443279e1ff0f1e19cc1fc -->
# Generated executable contract

Do not edit. Run `python3 scripts/skill_contract.py`.

```json
{
  "arguments": [
    {
      "choices": [
        "tuck-box",
        "miura-ori",
        "hex-petal",
        "diamond-box",
        "zero-glue-tray",
        "gable-box",
        "pillow-box",
        "crash-lock-box",
        "fefco-0201",
        "fefco-0427",
        "sleeve-tray",
        "food-box",
        "deer-base"
      ],
      "default": "tuck-box",
      "flags": [
        "--type"
      ],
      "type": "str"
    },
    {
      "choices": null,
      "default": null,
      "flags": [
        "--width"
      ],
      "type": "float"
    },
    {
      "choices": null,
      "default": null,
      "flags": [
        "--depth"
      ],
      "type": "float"
    },
    {
      "choices": null,
      "default": null,
      "flags": [
        "--height"
      ],
      "type": "float"
    },
    {
      "choices": null,
      "default": 40.0,
      "flags": [
        "--radius"
      ],
      "type": "float"
    },
    {
      "choices": null,
      "default": 0.5,
      "flags": [
        "--thickness"
      ],
      "type": "float"
    },
    {
      "choices": null,
      "default": "./output",
      "flags": [
        "--output-dir"
      ],
      "type": "str"
    },
    {
      "choices": [
        "presentation",
        "printer"
      ],
      "default": "presentation",
      "flags": [
        "--profile"
      ],
      "type": "str"
    },
    {
      "choices": null,
      "default": 3.0,
      "flags": [
        "--bleed-mm"
      ],
      "type": "float"
    },
    {
      "choices": null,
      "default": null,
      "flags": [
        "--spot-cut"
      ],
      "type": "str"
    },
    {
      "choices": null,
      "default": null,
      "flags": [
        "--spot-crease"
      ],
      "type": "str"
    },
    {
      "choices": null,
      "default": null,
      "flags": [
        "--spot-perforation"
      ],
      "type": "str"
    },
    {
      "choices": null,
      "default": null,
      "flags": [
        "--spot-bleed"
      ],
      "type": "str"
    },
    {
      "choices": null,
      "default": null,
      "flags": [
        "--spot-glue"
      ],
      "type": "str"
    }
  ],
  "bleed_mm": 3.0,
  "limits": [
    "Sampled source-derived continuity is not continuous-time or physical fit proof.",
    "Printer PDF: five spots, 1 pt; DXF: mm/y-up. Recipient import unverified.",
    "Allowance heuristic at 90 degrees is 0.45*t; mandated formula unresolved."
  ],
  "output_names": {
    "presentation": [
      "{name}.svg",
      "{name}.dxf",
      "{name}_viewer.html"
    ],
    "printer": [
      "{name}_printer.pdf",
      "{name}_printer.dxf"
    ]
  },
  "parameters": {
    "crash-lock-box": {
      "depth": 60.0,
      "height": 100.0,
      "thickness": 0.5,
      "width": 80.0
    },
    "deer-base": {
      "width": 200.0
    },
    "diamond-box": {
      "height": 80.0,
      "thickness": 0.5,
      "width": 50.0
    },
    "fefco-0201": {
      "depth": 150.0,
      "height": 120.0,
      "thickness": 0.5,
      "width": 200.0
    },
    "fefco-0427": {
      "depth": 150.0,
      "height": 60.0,
      "thickness": 0.5,
      "width": 200.0
    },
    "food-box": {
      "depth": 120.0,
      "height": 70.0,
      "thickness": 0.5,
      "width": 160.0
    },
    "gable-box": {
      "depth": 110.0,
      "height": 110.0,
      "thickness": 0.5,
      "width": 160.0
    },
    "hex-petal": {
      "height": 55.0,
      "radius": 40.0,
      "thickness": 0.5
    },
    "miura-ori": {},
    "pillow-box": {
      "depth": 40.0,
      "height": 110.0,
      "thickness": 0.5,
      "width": 90.0
    },
    "sleeve-tray": {
      "depth": 80.0,
      "height": 35.0,
      "thickness": 0.5,
      "width": 120.0
    },
    "tuck-box": {
      "depth": 50.0,
      "height": 120.0,
      "thickness": 0.5,
      "width": 80.0
    },
    "zero-glue-tray": {
      "depth": 70.0,
      "height": 30.0,
      "thickness": 0.5,
      "width": 100.0
    }
  },
  "profiles": [
    "presentation",
    "printer"
  ],
  "schema_version": 1,
  "source_hash": "95606d78ef780885c2a6483ae9966e8d2f7662758ce26688e14c9b763b2c3def",
  "spots": {
    "bleed": "Bleed",
    "crease": "CreaseLine",
    "cut": "CutContour",
    "glue": "GlueArea",
    "perforation": "Perforation"
  },
  "workflow_profile_limits": {
    "deer-base": [
      "presentation"
    ],
    "miura-ori": [
      "presentation"
    ]
  }
}
```
