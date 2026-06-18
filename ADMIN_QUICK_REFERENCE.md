# Admin Dashboard Quick Reference Card

## 🚀 Quick Access

- **Admin Login:** http://127.0.0.1:8000/admin/
- **Email:** admin@admin.com
- **Password:** admin1234

---

## 📊 Data Flow (What to Create First)

```
1. Clearance Levels
   ↓
2. Users
   ↓
3. Categories
   ↓
4. Products
   ↓
5. Robots (link to Products)
   ↓
6. Robot Specifications (link to Robots)
7. AI System Details (link to Robots)
8. Power Systems (link to Robots)
9. Usage Restrictions (link to Robots)
```

---

## 🔑 Field Meanings - Quick Lookup

### Clearance Levels
| Field | Example | Meaning |
|-------|---------|---------|
| Name | Military Clearance | Display name |
| Code | military | Internal code (lowercase, underscores) |
| Priority | 40 | Higher = more clearance (0-100) |
| Can Access Military | ✓ | Allows military robots |
| Is Active | ✓ | Enable/disable |

### Users
| Field | Example | Meaning |
|-------|---------|---------|
| Email | user@example.com | Login email (unique) |
| Username | username | Login username (unique) |
| Role | Buyer/Seller | User type |
| Is Active | ✓ | Can login |
| Is Staff | ✓ | Admin access |
| Is Seller Approved | ✓ | Can sell products |

### Products
| Field | Example | Meaning |
|-------|---------|---------|
| Seller | [Select from dropdown] | Who's selling |
| Title | ARES-X1 Drone | Product name |
| Price | 125000.00 | Cost in dollars |
| Status | Active/Draft | Visibility state |
| Category | [Select] | Product category |
| **UUID** | **[LEAVE BLANK]** | Auto-generated |

### Robots
| Field | Example | Meaning |
|-------|---------|---------|
| Product | [Select product] | Links to product |
| Robot Type | military_autonomous | Category of robot |
| Manufacturer | ARES Defense | Company name |
| Model Number | ARES-X1-2024 | Model ID |
| Requires Verification | ✓ | Needs user verification |
| Is Restricted | ✓ | Limited access |
| **UUID** | **[LEAVE BLANK]** | Auto-generated |

### Usage Restrictions
| Field | Example | Meaning |
|-------|---------|---------|
| Robot | [Select robot] | Which robot |
| Restriction Level | military_only | Access level |
| Requires Verification | ✓ | User must be verified |
| Requires Export License | ✓ | Export controls apply |

---

## ⚠️ Common Mistakes to Avoid

1. ❌ **Typing UUID manually** → ✓ Leave blank
2. ❌ **Typing seller email in seller field** → ✓ Use dropdown
3. ❌ **Creating robot before product** → ✓ Product first, then robot
4. ❌ **Forgetting to set Is Restricted** → ✓ Check for military robots
5. ❌ **Leaving Status as Draft** → ✓ Change to Active to show

---

## 🎯 Typical Values Reference

### Robot Types
- `consumer_drone` - Personal drones
- `commercial_drone` - Business drones  
- `military_autonomous` - Military systems
- `industrial_robot` - Factory robots
- `service_robot` - Service industry
- `humanoid_robot` - Human-like robots

### Restriction Levels
- `none` - No restrictions
- `clearance_required` - Needs clearance
- `military_only` - Military personnel only
- `export_controlled` - Export restricted

### Product Status
- `draft` - Not visible (testing)
- `active` - Visible and purchasable
- `paused` - Temporarily hidden
- `out_of_stock` - No inventory

---

## 🔄 Quick Workflow Example

**Creating a Military Robot (5 minutes):**

1. Admin → Products → Products → Add Product
   - Title: "ARES-X1"
   - Price: 125000.00
   - Status: Active
   - Category: Military-Grade Robots
   - Save

2. Admin → Products → Robots → Add Robot
   - Product: Select "ARES-X1"
   - Robot Type: military_autonomous
   - Manufacturer: ARES Defense
   - Model: ARES-X1-2024
   - Requires Verification: ✓
   - Is Restricted: ✓
   - Save

3. Admin → Products → Usage Restrictions → Add
   - Robot: Select "ARES-X1"
   - Restriction Level: military_only
   - Requires Verification: ✓
   - Save

**Done!** ✅

---

## 📞 Need Help?

Refer to **ADMIN_COMPLETE_GUIDE.md** for:
- Detailed field explanations
- Step-by-step instructions
- Complete examples
- Troubleshooting tips









