![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

# SpaceSwitch Tool for Autodesk Maya

![UI](https://github.com/user-attachments/assets/cde54c7d-7160-4681-b5f3-1cb2ec6a5884)

---

## Overview

**SpaceSwitch** is a lightweight animation utility designed to help animators manage **gimbal lock**, restructure rotational behaviour, and perform safe world-space animation adjustments inside Autodesk Maya.

Inspired by workflow concepts shared by **Richard Lico** via [Animation Sherpa](https://www.animationsherpa.com/), this tool introduces a **locator-based animation buffering workflow** that allows motion to be temporarily transferred, adjusted, and cleanly baked back to controllers.

This enables animators to refine motion without damaging original animation curves or modifying rig structures.

> ⚠️ This tool is intended for educational and personal workflow use.

---

## Features

- Avoid, fix, or *creatively work around* gimbal lock issues
- World-space animation buffering using locator drivers
- Supports all six Maya rotation orders
- Enables pivot restructuring and large motion offsets
- Non-destructive animation adjustment workflow
- Lightweight execution suitable for polish stage work
- Shelf button integration for quick access

---

## Workflow Concept

### Animation Buffer via Locator

The tool transfers animation from selected controller(s) onto generated locator(s).

These locators act as **temporary world-space animation drivers**, allowing animators to:

- isolate unstable rotations  
- adjust motion without hierarchy constraints  
- restructure spatial relationships safely  
- stabilise motion arcs  

---

### Rotation Order Experimentation

Locators can be created using different rotation orders.

This allows animators to:

- test rotational stability quickly  
- reduce curve flipping or axis fighting  
- rebuild animation behaviour with improved axis evaluation  

---

### Manual Adjustment Mode

Animators can optionally spawn locators manually to:

- change pivot influence  
- introduce major offsets  
- correct directional motion  
- "cheat" difficult polish situations  

Once adjustments are complete, animation can be baked back onto controllers.

---

### Clean Bake Restoration

After refinement:

- locator animation is baked  
- constraints are removed  
- improved animation is restored to original controllers  

Resulting in:

- cleaner rotation curves  
- improved motion readability  
- reduced gimbal artefacts  

---

## Installation

1. Open **Autodesk Maya**
2. Drag and drop `SpaceSwitch_Install.mel` into the Maya viewport
3. A shelf icon will be created automatically
4. Click the icon to launch the tool

---

## Usage

1. Select controller(s)
2. Choose rotation order or workflow option
3. Generate locator driver(s)
4. Adjust motion / pivot / spacing as needed
5. Bake animation back to controller(s)

---

## Credits & Reference

- **Richard Lico** — Original methodology inspiration  
  https://www.animationsherpa.com/

All credit for the original gimbal lock concepts belongs to the original author.

---

## Feedback & Contributions

This is an evolving personal workflow tool.

Feedback, production suggestions, and improvement ideas are welcome.

If you encounter issues or would like to suggest enhancements, feel free to open an issue or reach out.

---

## License

Provided **as-is** for personal and educational use.
