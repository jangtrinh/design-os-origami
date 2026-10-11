---
id: creative-packaging-taxonomy
title: "Creative Origami Packaging Taxonomy: 5 Structural Families & 300+ Industry Applications"
domain: "packaging-engineering"
description: "Comprehensive 5-family structural taxonomy mapping 300+ creative origami packaging applications across cosmetics, luxury gifts, confectionery, perfume, and eco-minimalism."
when: ["cataloging packaging structures", "selecting origami carton geometries", "designing structural packaging", "evaluating folding carton styles", "zero-glue sustainable packaging"]
trust_tier: "draft"
version: "1.0.0"
quarantine:
  is_external_untrusted: false
---

# Creative Origami Packaging Taxonomy: 5 Structural Families & 300+ Industry Applications

## Draft Provenance Notice

This taxonomy is draft guidance. Its former verified status, source hash and
source licence claim lacked supporting evidence and have been removed.
Application ideas are not validated CAD models; cited references do not grant
permission to reproduce third-party material.

## Purpose
Establishes an engineering taxonomy of 300+ origami-inspired structural packaging architectures categorized across 5 primary geometric families. It provides structural designers, packaging engineers, and CAD automation algorithms with exact kinematics, sector angles, board caliper constraints, friction interlocks, and industry-specific deployment rules across cosmetics, luxury gifts, confectionery, perfume, and eco-minimalist mono-material cartons.

## When to Use / When NOT
### ALLOWED (When to Use)
- Selecting geometric topologies and folding mechanisms for primary, secondary, and tertiary retail packaging.
- Developing parametric CAD templates for folding cartons with zero-glue mechanical interlocks.
- Designing high-tactile unboxing experiences for luxury cosmetics, haute parfumerie, artisanal confectionery, and premium gifting.
- Engineering single-sheet mono-material paperboard packaging adhering to circular economy regulations (e.g., EU PPWR 2025/2030, plastic-free directives).
- Determining score allowance formulas, relief notch profiles, and grain orientation for complex 3D polyhedra.

### NOT ALLOWED (When NOT to Use)
- High-speed form-fill-seal (FFS) flexible pouch packaging (use continuous web flexible packaging standards).
- Deep-drawn metal canisters, rigid blown glass containers, or thermoformed plastic blisters.
- Structural calculations for palletized corrugated bulk shipping containers exceeding $5.0\text{mm}$ BC flute thickness without full FEA structural simulation.

## Core Knowledge Content
<!-- ease:source status="unverified" -->

### 1. Architectural Overview of the 5 Origami Packaging Families

Origami packaging synthesizes planar non-Euclidean geometry, rigid facet kinematics, and paperboard fiber mechanics to create 3D enclosures from a single flat sheet. The 300+ cataloged structures are organized into 5 primary geometric families:

```
                                  ORIGAMI PACKAGING TAXONOMY
                                               │
         ┌──────────────────┬──────────────────┼──────────────────┬──────────────────┐
         │                  │                  │                  │                  │
    [FAMILY 1]         [FAMILY 2]         [FAMILY 3]         [FAMILY 4]         [FAMILY 5]
    Polyhedral &      Tessellated &       Radial, Iris &     Zero-Glue &        Modular &
    Faceted Cartons   Kinetic Bellows    Blooming Twists    Self-Locking      Kinetic Reveal
   (Apps 001–060)     (Apps 061–120)     (Apps 121–180)     (Apps 181–240)    (Apps 241–300+)
```

---

### Family 1: Polyhedral & Faceted Origami Packaging (Applications 001–060)
*Geometric Definition*: Enclosures whose volumetric envelope is bounded by planar triangular, trapezoidal, or polygonal facets joined along alternating mountain and valley diagonal crease lines.
*Kinematic Behavior*: Non-orthogonal dihedral folding angles $\psi \in [45^\circ, 140^\circ]$; high torsional rigidity from triangular facet triangulation.

| ID | Geometric Topology | Industry Vertical | Application Description | Closure / Interlock | Substrate & Caliper |
|:---|:---|:---|:---|:---|:---|
| 001 | Hexagonal Bipyramid | Perfume | Faceted teardrop flacon secondary carton | Friction tuck apex tab | FBB 350 gsm (0.45mm) |
| 002 | Truncated Octahedron | Cosmetics | Anti-aging night cream faceted jar pod | Snap-fit base ring | SBS 380 gsm (0.50mm) |
| 003 | Rhombic Dodecahedron | Luxury Gifts | Fine jewelry gemstone ring display box | Magnetic facet flap | Black core board 400 gsm |
| 004 | Pentagonal Antiprism | Perfume | Eau de Parfum bottle sculptural plinth | Self-tucking collar | Kraft 300 gsm (0.42mm) |
| 005 | Icosahedral Segment | Cosmetics | Single-use eye serum ampoule cluster | Tear-perforated strip | Virgin SBS 280 gsm |
| 006 | Tetrahedral Pyramid | Confectionery | Artisanal chocolate truffle portion pack | Pull-ribbon apex eyelet | Recycled Kraft 250 gsm |
| 007 | Triangulated Obelisk | Perfume | Tall flacon monolith with faceted shoulder | Interlocking base star | FBB 380 gsm (0.52mm) |
| 008 | Hexagonal Trapezohedron | Luxury Gifts | Swiss mechanical watch presentation vault | Rollover double-wall facet | Premium cotton 450 gsm |
| 009 | Octagonal Truncated Cone | Cosmetics | Mineral powder loose compact container | Inner friction plug | Kraft 350 gsm (0.48mm) |
| 010 | Triacontahedron Segment | Luxury Gifts | Haute joaillerie diamond necklace casket | Concealed slide clip | Pure virgin cellulose 420 gsm |
| 011 | Hexagonal Prismatic Twist | Perfume | Travel atomizer twist-action outer shell | Helical snap lock | Heavyweight SBS 350 gsm |
| 012 | Triangular Prismatic Box | Confectionery | Nougat bar diagonal split gift sleeve | Side flap friction slot | Food-grade kraft 280 gsm |
| 013 | Truncated Tetrahedron | Eco-Minimalism | Zero-plastic solid soap exfoliating bar | Single-tuck bottom | Unbleached kraft 300 gsm |
| 014 | Diamond Faceted Pillow | Cosmetics | Facial sheet mask contoured luxury pouch | Curved score snap ends | Metalized PET/SBS 320 gsm |
| 015 | Deltoidal Icositetrahedron | Luxury Gifts | Anniversary commemorative coin pod | Nested twin-shell | Velvet-laminated 400 gsm |
| 016 | Pentagonal Dipyramid | Confectionery | Artisanal marzipan seasonal favor box | String-tie facet apex | Pearlescent 280 gsm |
| 017 | Octahedral Solitaire Pod | Perfume | Luxury solid perfume balm jewel case | Interlocking diamond tabs | Rigid bleached board 350 gsm |
| 018 | Asymmetric Faceted Monolith | Cosmetics | Foundation glass bottle protective housing | Integral cushioning facet | E-flute corrugated (1.5mm) |
| 019 | Dodecahedral Ballotin | Confectionery | 12-piece gourmet praline sampler sphere | Equatorial latch tab | Food-contact FBB 320 gsm |
| 020 | Truncated Hexagonal Dome | Luxury Gifts | Rare collector fountain pen case | Hinged faceted canopy | Soft-touch laminated 380 gsm |
| 021 | Rhombic Triacontahedron | Perfume | Limited-edition crystal flacon pedestal | Recessed locking plinth | Heavyweight SBS 450 gsm |
| 022 | Chevron-Faceted Column | Cosmetics | Multi-shade lip gloss vertical display | Slide-out faceted sleeve | Cast-coated board 300 gsm |
| 023 | Stellated Octahedron | Luxury Gifts | Holiday diamond pendant star ornament box | Intermeshing star points | Metallic foil card 320 gsm |
| 024 | Triangulated Torus Segment | Confectionery | Macaron radial ring assortment carrier | Center rosette lock | Food-safe unbleached 270 gsm |
| 025 | Snub Cube Origami Pod | Perfume | Fragrance solid stick magnetic applicator shell | Integral paper friction hinge | Mineral paperboard 350 gsm |
| 026 | Hexagonal Faceted Urn | Cosmetics | Herbal bath salt luxury decanter carton | Fold-down facet collar | Wet-strength kraft 350 gsm |
| 027 | Rhomboid Slider Box | Luxury Gifts | Cufflink dual-vault sliding jewel box | Internal pop-up easel | Rigid paperboard 400 gsm |
| 028 | Truncated Hexagonal Column | Perfume | Cylindrical bottle anti-roll transport shell | Corner lock score tabs | Micro-flute F-board (0.8mm) |
| 029 | Faceted Diamond Ring Box | Luxury Gifts | Engagement solitaire pop-up ring pavilion | Auto-erect faceted cradle | Linen-textured 350 gsm |
| 030 | Triangulated Clamshell | Cosmetics | Organic eyeshadow quad compact casing | Friction bevel clasp | Post-consumer kraft 320 gsm |
| 031 | Octagonal Faceted Cup | Confectionery | Handcrafted dipped fruit serving cup | Self-erecting base | Greaseproof SBS 260 gsm |
| 032 | Helical Faceted Tower | Perfume | Artisanal room diffuser & reed bouquet | Interlocking helical ribs | Recycled corrugated 1.2mm |
| 033 | Diamond Prism Duo | Cosmetics | Day/Night double serum dual-chamber pack | Central spine flex hinge | Dual-ply SBS 400 gsm |
| 034 | Truncated Pyramid Box | Luxury Gifts | Silk pocket square or foulard presentation | Envelope fold-over flap | Textured art board 300 gsm |
| 035 | Bi-Pyramidal Capsule | Confectionery | Single origin cocoa bean degustation box | Pinch-to-open apex | Direct food contact 280 gsm |
| 036 | Faceted Hex Flacon Cage | Perfume | Fragrance flacon drop-tested suspension | Cantilevered internal facet | Unbleached kraft 350 gsm |
| 037 | Triangular Diamond Tube | Cosmetics | Mineral sunscreen stick ergonomic tube | Push-up bottom facet | Compostable paper 320 gsm |
| 038 | Decagonal Faceted Base | Luxury Gifts | Crystal paperweight heavy display pedestal | Weighted hollow-wall fold | Multi-layer SBS 500 gsm |
| 039 | Inverted Pyramid Stand | Perfume | Upside-down luxury bottle architectural stand | Locking cross-struts | Stiff bleached board 420 gsm |
| 040 | Faceted Dome Cloche | Confectionery | Wedding dessert individual gateau dome | Flange locking ring | Clear-windowed SBS 300 gsm |
| 041 | Diamond Zig-Zag Pillar | Cosmetics | Retractable eyeliner protective sheath | Spiral score lock | Dense virgin kraft 280 gsm |
| 042 | Hexagonal Gem Pouch | Luxury Gifts | Loose gem certified valuation parcel | Origami safety envelope | Glassine-lined kraft 220 gsm |
| 043 | Truncated Icosahedron Sphere | Confectionery | Football-themed festive chocolate sphere | Snap-in polygonal tabs | Caliper 0.40mm FBB |
| 044 | Faceted Hex Coffret | Perfume | 5-piece discovery sample vial flight | Integrated vial cradles | Rigid folding boxboard 380 gsm |
| 045 | Triangular Bipyramid | Eco-Minimalism | Natural solid shampoo travel container | Water-resistant bio-seal | Biodegradable hemp 300 gsm |
| 046 | Rhombic Prism Carton | Cosmetics | Mascara curved-wand protective carton | Asymmetric tuck closure | Silk-finish card 300 gsm |
| 047 | Trapezoidal Accordion Box | Luxury Gifts | Luxury silk tie tiered unboxing carton | Expanding lateral facets | Satin-laminated 350 gsm |
| 048 | Faceted Petal Pod | Confectionery | Handcrafted Turkish delight jewel box | Four-petal overlap apex | Metallic pearl card 260 gsm |
| 049 | Octagonal Faceted Flask | Perfume | Pocket spray flacon slim faceted shell | Push-through tab lock | SBS 320 gsm (0.40mm) |
| 050 | Truncated Star Prism | Luxury Gifts | VIP invitation medal keepsake box | Magnetic star closure | Velvet flock board 400 gsm |
| 051 | Triangular Faceted Wedge | Cosmetics | Makeup sponge ventilated drying carton | Perforated facet vents | Wet-strength kraft 280 gsm |
| 052 | Hexagonal Diamond Lantern | Luxury Gifts | Scented candle faceted lantern enclosure | Cut-out facet illumination | Fire-retardant card 350 gsm |
| 053 | Faceted Egg Container | Confectionery | Easter artisan chocolate egg cocoon | Two-part interlocking shell | Food-grade kraft 320 gsm |
| 054 | Diamond Faceted Mailer | Eco-Minimalism | Plastic-free luxury retail e-commerce mailer | Tamper-evident pull tab | E-flute kraft (1.6mm) |
| 055 | Stellated Cube Keepsake | Luxury Gifts | Heritage brooch velvet-cushioned box | Corner tuck interlocking | Bookbinding cloth/board 450 gsm |
| 056 | Asymmetric Facet Sleeve | Cosmetics | Contour palette angled slide sleeve | Friction-glide track | Heavyweight SBS 350 gsm |
| 057 | Polyhedral Bottle Jacket | Perfume | Protective transit jacket for fragile flacons | Spring-facet absorption | Microflute board 1.0mm |
| 058 | Faceted Pyramid Ballot | Confectionery | Single marron glacé confection pod | Interlocking wing apex | Gold-hotstamped 280 gsm |
| 059 | Hexagonal Prism Pedestal | Luxury Gifts | Diamond bracelet showcase cylinder | Auto-expanding base ring | Rigid paperboard 420 gsm |
| 060 | Octagonal Facet Vault | Perfume | Exclusive fragrance numbered edition box | Hidden hinge facet lock | Matte-black solid board 500 gsm |

---

### Family 2: Tessellated, Corrugated & Kinetic Folding (Applications 061–120)
*Geometric Definition*: Repeating planar tessellations (Miura-ori, Yoshimura diamond pattern, Waterbomb base, Resch patterns) imparting dynamic collapse, auxetic properties, and shock absorption.
*Kinematic Behavior*: Negative Poisson's ratio (auxetics), programmable volumetric compression ratios exceeding 4:1.

| ID | Geometric Topology | Industry Vertical | Application Description | Closure / Interlock | Substrate & Caliper |
|:---|:---|:---|:---|:---|:---|
| 061 | Miura-ori Protective Wrap | Perfume | Cushioning wrap eliminating bubble wrap | Elastic paper sleeve | Heavy unbleached kraft 120 gsm |
| 062 | Waterbomb Collapsible Box | Cosmetics | Travel face wash compact folding cube | Pop-open corner lock | Waterproof synthetic 200 gsm |
| 063 | Yoshimura Buckling Sleeve | Perfume | Cylindrical bottle impact-absorbing jacket | Cylindrical glue seam | Recycled testliner 180 gsm |
| 064 | Resch Star Vault Envelope | Luxury Gifts | Flat-to-3D expanding gift card presentation | Self-opening spring crease | Pure cotton card 250 gsm |
| 065 | Flasher Tessellation Disk | Cosmetics | Solid blush round compact twist cover | Spiral radial fold | Polypropylene-coated 220 gsm |
| 066 | Accordion Bellows Sleeve | Confectionery | Expandable macaron gift cylinder (6 to 12 pcs) | Slide-lock collar ring | Food-approved card 250 gsm |
| 067 | Diamond Herringbone Wrap | Eco-Minimalism | Fragile glassware zero-plastic packaging wrap | Self-nesting ridges | 100% post-consumer 150 gsm |
| 068 | Miura-ori Fold-Out Map Box | Luxury Gifts | Heritage brand narrative storytelling coffret | Magnetic side spine | Linen-backed paper 200 gsm |
| 069 | Waterbomb Octagonal Tray | Confectionery | Party dessert serving platter, pops flat | Snap-together tabs | Grease-resistant SBS 300 gsm |
| 070 | Diagonal Pleat Tube | Cosmetics | Eyebrow pencil expandable carry tube | Twist-and-lock cap | Virgin kraft 240 gsm |
| 071 | Ron Resch Triangular Dome | Perfume | Haute parfumerie domed outer presentation | Concealed rim lock | Laminated card 350 gsm |
| 072 | Yoshimura Hexagonal Tube | Eco-Minimalism | Wine & olive oil courier shockproof sleeve | End tuck star flaps | Kraft corrugated 1.2mm |
| 073 | Hexagonal Waterbomb Box | Cosmetics | Cleansing balm jar expandable box | Push-down base lock | Matte coated SBS 320 gsm |
| 074 | Chevron Pleat Envelope | Luxury Gifts | Silk scarf flat-pack expander envelope | Interlocking flap | Textured deckle paper 280 gsm |
| 075 | Miura-ori Solar Pouch | Eco-Minimalism | Solar battery / electronics retail box | Integrated fold latch | Uncoated chipboard 260 gsm |
| 076 | Auxetic Diamond Sleeve | Perfume | Perfume bottle thermal & drop shield | Expanding grid fit | Perforated kraft 200 gsm |
| 077 | Double Waterbomb Capsule | Confectionery | Twin-compartment gourmet jelly bean pod | Center pinch divider | Food-grade barrier board 250 gsm |
| 078 | Curved Crease Bellows | Cosmetics | Liquid foundation shock-absorbing cradle | Suspended facet net | Virgin SBS 300 gsm |
| 079 | Tessellated Star Box | Luxury Gifts | Holiday diamond earring reveal box | Magnetic point closures | Shimmer paperboard 320 gsm |
| 080 | Accordion Stepped Box | Confectionery | Stepped tier chocolate degustation sampler | Auto-sliding tier linkage | Rigid folding card 350 gsm |
| 081 | Miura-ori Tray Insert | Perfume | Multi-vial sampler zero-plastic separator | Friction-slotted matrix | Recycled craft card 220 gsm |
| 082 | Yoshimura Collapsible Cup | Eco-Minimalism | Single-use festival zero-waste cup | Waterproof heat seal | PEFC-certified bamboo 260 gsm |
| 083 | Waterbomb Gift Bag | Luxury Gifts | Self-standing faceted paper shopping bag | Fold-over handles | Reinforced kraft 180 gsm |
| 084 | Hexagonal Pleated Lantern | Confectionery | Pastry shop seasonal lantern carrier | Twisted rope closure | Semi-translucent vellum 200 gsm |
| 085 | Triangular Herringbone Case | Cosmetics | Makeup brush travel case with roll-up wrap | Ribbon wrap cord | Washable kraft paper 300 gsm |
| 086 | Kinetic Expanding Coffret | Luxury Gifts | Grand unboxing jewelry presentation suite | Counterbalanced lever folds| Rigid greyboard + art paper |
| 087 | Miura Wine Carrier | Eco-Minimalism | Dual-bottle flat-to-3D transport tote | Integral die-cut handles | Heavy kraft board 400 gsm |
| 088 | Diagonal Rib Tube | Perfume | Atomizer cylindrical shipping tube | Cap friction detent | Spiral wound / creased kraft |
| 089 | Resch Hexagonal Ring Box | Luxury Gifts | Geometric petal ring presentation box | Spring-action hinge | Silk art card 300 gsm |
| 090 | Waterbomb Pop-Up Card | Cosmetics | Cosmetic launch VIP invitation & sample | Flat-mailer snap open | Coated 2-side SBS 350 gsm |
| 091 | Diamond Pleat Bottle Sleeve| Confectionery | Artisanal vinegar & liqueur protective jacket | Base wrap lock | Unbleached fluting 160 gsm |
| 092 | Auxetic Netting Sleeve | Cosmetics | Glass pipette dropper safety sleeve | Self-contracting grip | Die-cut expandable kraft 140 gsm |
| 093 | Accordion Folder Box | Luxury Gifts | Leather goods certificate & warranty holder | Multi-pocket expander | Heavy parchment 240 gsm |
| 094 | Yoshimura Candle Sleeve | Eco-Minimalism | Ceramic candle vessel zero-waste shipper | End flap cushion | Recycled corrugated 1.5mm |
| 095 | Miura-ori Soap Wrapper | Eco-Minimalism | Organic botanical cold-process soap wrap | Fold-tuck envelope | Seed-infused paper 120 gsm |
| 096 | Kinetic Star Box | Confectionery | Christmas confectionery star box | Sliding arm interlock | Red dyed-through pulp 280 gsm |
| 097 | Hexagonal Bellows Carton | Perfume | Eau de Cologne tactile concertina carton | Push-in rim lock | Textured matte SBS 320 gsm |
| 098 | Zig-Zag Display Stand | Cosmetics | Retail counter lipstick stepped display | Interlocking tabs | High-density F-flute 1.0mm |
| 099 | Collapsible Waterbomb Tub | Confectionery | Gourmet popcorn expandable cinema tub | Grease-resistant fold base | Barrier-coated board 280 gsm |
| 100 | Kinetic Diamond Purse | Luxury Gifts | Evening minaudière paper clutch gift box | Concealed snap fastener | Embossed leatherette card 350 gsm |
| 101 | Fold-Flat Gift Basket | Eco-Minimalism | Gourmet farm-to-table fruit & wine basket | Mechanical locking corners| Heavy unbleached board 450 gsm |
| 102 | Miura-ori Perfume Insert | Perfume | Suspension cushion for heavy crystal bottle | Integral friction wings | Rigid kraft 280 gsm |
| 103 | Yoshimura Tube Mailing Box | Eco-Minimalism | Triangular kinetic postage tube for posters | Tape-free self-locking end | E-flute corrugated 1.5mm |
| 104 | Waterbomb Lip Balm Pack | Cosmetics | 3-pack organic lip balm folding display | Pop-out front blisters | SBS 300 gsm (0.38mm) |
| 105 | Pleated Cake Carrier | Confectionery | High-profile wedding cake slice carrier | Top carry handle lock | Stiff greaseproof board 350 gsm |
| 106 | Auxetic Paper Bubble Pouch | Eco-Minimalism | E-commerce cosmetic parcel mailer | Peel-and-seal dry glue | Dual-layer micro-creped 160 gsm |
| 107 | Kinetic Expanding Tray | Luxury Gifts | Watch strap collection multi-tier organizer | Parallel linkage folds | Rigid bookbinding greyboard |
| 108 | Resch Pattern Lamp Carton | Luxury Gifts | Origami lampshade packaging & shade combo | Tear-away packaging rim | Translucent poly-paper 200 gsm |
| 109 | Miura Mask Dispenser | Cosmetics | 30-day facial sheet mask pop-up dispenser | Spring-loaded bottom fold | Recycled cartonboard 320 gsm |
| 110 | Herringbone Bottle Mailer | Perfume | Single-bottle zero-damage shipping carton | Anti-crush lateral ribs | Double-wall corrugated 3.0mm |
| 111 | Yoshimura Hexagonal Jar Box| Confectionery | Honey pot hexagonal facet cocoon | Top flower closure | Kraft board 300 gsm |
| 112 | Accordion Tea Sachet Box | Confectionery | 20-compartment artisanal tea bag caddy | Pull-out bellows spine | Uncoated botanical card 260 gsm |
| 113 | Waterbomb Jewelry Envelope | Luxury Gifts | Fine pearl bracelet origami presentation | Silk cord tie | Handmade washi paper 180 gsm |
| 114 | Diamond Kinetic Clamshell | Cosmetics | Compact powder refillable shell | Snap-detent latch | Molded cellulose pulp 1.2mm |
| 115 | Miura-ori Face Towel Pack | Eco-Minimalism | Compressed bamboo face towel travel carton | Push-through dispensing | Biodegradable PLA/paper 240 gsm |
| 116 | Pleated Chocolate Envelope | Confectionery | Single-origin chocolate tablet luxury sleeve | Side-sliding envelope | Textured cocoa-husk paper 220 gsm |
| 117 | Hexagonal Kinetic Vase Box | Luxury Gifts | Preserved rose luxury stem presentation | Auto-erecting vase base | Cast-coated art card 380 gsm |
| 118 | Auxetic Wine Bottle Sleeve | Eco-Minimalism | Champagne bottle export transit protector | Conforming mesh folds | Recycled newsprint fluting |
| 119 | Kinetic Stepped Sampler | Perfume | Olfactory flight 6-sample scent strip card | Accordion pop-up easel | High-absorption card 300 gsm |
| 120 | Yoshimura Protective Boot | Perfume | Fragrance tester bottle safety base bumper | Snap-fit bottom rim | Stiff unbleached kraft 280 gsm |

---

### Family 3: Radial, Blooming & Iris Twisting Closures (Applications 121–180)
*Geometric Definition*: Rotational symmetry mechanisms where overlapping curved or angled sector flaps close via continuous torsion, forming an iris aperture, rosette, or blooming floral petal reveal.
*Kinematic Behavior*: Single-degree-of-freedom rotational actuation; torque $\tau$ applied to outer rim rotates flaps into self-locking interlock without adhesives.

| ID | Geometric Topology | Industry Vertical | Application Description | Closure / Interlock | Substrate & Caliper |
|:---|:---|:---|:---|:---|:---|
| 121 | 6-Petal Blooming Lotus Box | Luxury Gifts | Engagement ring surprise bloom unveiling | Center interlocking petals| Pearlized folding card 320 gsm |
| 122 | 8-Blade Iris Aperture Cap | Perfume | Bottle cap aperture mechanism, twists open | Rotational spiral blade lock| Rigid card laminate 300 gsm |
| 123 | Hexagonal Twist-Lock Box | Cosmetics | Luxury face cream jar presentation box | Torsion-twist top folds | Heavy SBS 350 gsm (0.46mm) |
| 124 | Star Rosette Cookie Box | Confectionery | Butter cookie tin replacement paperboard box | Star-creased interlocking | Food-grade kraft 300 gsm |
| 125 | Octagonal Pinwheel Carton | Cosmetics | Bath bomb effervescent sphere gift pack | Center pinwheel overlap | Wet-strength card 280 gsm |
| 126 | Spiral Vortex Cup | Confectionery | Gelato takeaway origami tub with twist lid | Helical fold-down seal | PEFC-barrier board 260 gsm |
| 127 | 12-Facet Iris Dome | Luxury Gifts | Haute horlogerie presentation dome | Multi-blade rotary aperture| High-finish rigid card 400 gsm |
| 128 | Petal Blossom Powder Box | Cosmetics | Loose setting powder leak-proof twist pack | Internal paper seal diaphragm| SBS 300 gsm + wax coat |
| 129 | Triangular Twist Top Box | Confectionery | Artisanal caramel trio gift wedge | 3-wing torsion lock | Food-safe kraft 250 gsm |
| 130 | 5-Petal Cherry Blossom Box | Luxury Gifts | Japanese souvenir sweet presentation | Interlocking calyx base | Japanese Kozo art card 220 gsm |
| 131 | Helical Twist Bottle Collar | Perfume | Champagne flacon neck tamper collar | Tear-strip spiral release | Metallic foil laminated 240 gsm |
| 132 | Radial Starburst Envelope | Cosmetics | Serum sample sachet presentation folder | Center sunburst latch | Heavy uncoated stock 280 gsm |
| 133 | Octagonal Twist Drum | Confectionery | Festive chocolate bonbon sharing drum | Top & bottom torsion caps | Stiff cartonboard 350 gsm |
| 134 | Curvilinear Petal Bloom | Perfume | Limited-edition flacon grand reveal coffret | Curved crease flower pop | Virgin SBS 380 gsm |
| 135 | 4-Blade Windmill Carton | Eco-Minimalism | Zero-tape e-commerce subscription box | Interlocking windmill wings| Fluted kraft corrugated 1.2mm |
| 136 | Iris Diaphragm Lens Case | Luxury Gifts | High-end eyewear cleaning kit & case | Camera-shutter twist closure| Recycled leather paper 320 gsm |
| 137 | Pentagonal Spiral Caddy | Confectionery | Loose leaf artisan green tea canister | Double-twist aroma seal | Aluminum-barrier card 300 gsm |
| 138 | Blooming Rose Ring Case | Luxury Gifts | Proposal ring box, rose unfolds on opening | Kinematic petal linkage | Silk paper over board 250 gsm |
| 139 | Hexagonal Pinwheel Tub | Cosmetics | Body butter wide-mouth tub | Friction pinwheel lock | Grease-barrier board 320 gsm |
| 140 | Vortex Twist Sachet | Eco-Minimalism | Single-dose laundry detergent powder pouch | Dissolvable pinch seal | Bio-polymer coated paper 180 gsm |
| 141 | Radial Sunburst Box | Confectionery | Spun-sugar confection holiday keepsake | Central rosette detent | Gold foil stamped SBS 300 gsm |
| 142 | 8-Petal Dahlia Coffret | Luxury Gifts | High jewelry brooch showcase box | Layered petal bloom | Multi-tier duplex board 380 gsm |
| 143 | Twist-Top Perfume Cylinder | Perfume | Spray bottle outer protective column | Spiral cam-lock top | Spiral core with creased end |
| 144 | Petal Flap Soap Carton | Eco-Minimalism | Zero-glue botanical soap bar box | Four-petal center tuck | Unbleached compostable 280 gsm |
| 145 | Hexagonal Rosette Ballotin | Confectionery | Luxury chocolate truffle 4-piece box | Interlocking crown flaps | Cast-coated gloss card 280 gsm |
| 146 | Concentric Twist Collar | Perfume | Scented candle snuffer lid & box | Double-walled twist lock | Fire-treated rigid board 350 gsm |
| 147 | Curving Blade Iris Tub | Cosmetics | Solid exfoliating scrub tub | Cam-lock rotary lid | Water-repellent kraft 300 gsm |
| 148 | 6-Point Star Bloom Box | Luxury Gifts | Pearl earring pair holiday keepsake | Star-point latch | Metallic iridescent 300 gsm |
| 149 | Windmill Pastry Carrier | Confectionery | Individual tartelette bakery box | Integrated finger carry loop| White virgin FBB 300 gsm |
| 150 | Spiral Apex Pyramid | Luxury Gifts | Commemorative medallion presentation | Pinch-twist apex lock | Velvet laminate 350 gsm |
| 151 | Radial Petal Candle Cloche | Luxury Gifts | Aromatherapy candle reveal cloche | Flower bloom lift-off | Heavyweight cotton board 400 gsm |
| 152 | 8-Blade Turbine Box | Cosmetics | Sheet mask 7-day treatment cycle tower | Rotary dispensing bottom | Coated greyback 350 gsm |
| 153 | Hexagonal Iris Dispenser | Confectionery | Mint & lozenge sliding iris dispenser | Click-action rotary opening | Food-grade SBS 280 gsm |
| 154 | Blooming Tulip Perfume Pod | Perfume | Solid perfume pendant travel casing | Magnetic flower petals | Rigid art paper 300 gsm |
| 155 | Twist-Close Dry Food Pouch | Eco-Minimalism | Organic spice zero-plastic retail carton | Interlocking twist crown | Glassine-lined kraft 200 gsm |
| 156 | Pinwheel Macaron Tower | Confectionery | 3-tier round macaron tower with twist caps | Center dowel lock | Rigid SBS foodboard 320 gsm |
| 157 | Star-Twist Serum Box | Cosmetics | Concentrated vitamin C ampoule box | 5-point star torsion top | Metallic barrier SBS 320 gsm |
| 158 | Rotary Shutter Box | Luxury Gifts | Luxury cufflinks presentation box | Shutter aperture dial | Premium black duplex 380 gsm |
| 159 | Petal Envelope Wallet | Luxury Gifts | Gift card & voucher origami wallet | Floral fold-in flaps | Heavy linen card 240 gsm |
| 160 | Spiral Flute Bottle Tube | Perfume | Rare single malt whisky sample tube | Continuous spiral crease | Heavy craft cylinder 450 gsm |
| 161 | 10-Blade Iris Gift Jar | Confectionery | Handmade hard candy presentation drum | Polyhedral iris top | Clear-aperture card 300 gsm |
| 162 | Blooming Waterlily Case | Luxury Gifts | Jade bangle bracelet showcase pod | Expanding waterlily folds | Silk-laminated card 320 gsm |
| 163 | Hex Twist Mask Carton | Cosmetics | Clay mask powder & mixing spoon kit | Top twist handle lock | Unbleached kraft 350 gsm |
| 164 | Starburst Favor Box | Confectionery | Wedding sugared almond gift star | Intermeshing star crest | Pearlized card 250 gsm |
| 165 | Curvilinear Iris Decanter | Perfume | Crystal flacon presentation box | Smooth curved fold iris | Soft-touch laminated 400 gsm |
| 166 | 4-Petal Clover Box | Eco-Minimalism | Eco-conscious shampoo bar carton | Four-leaf clover lock | Recycled hemp card 280 gsm |
| 167 | Radial Fan Pastry Box | Confectionery | Croissant & Danish takeaway carrier | Fan-folding carry handle | Greaseproof kraft 260 gsm |
| 168 | Rotary Dial Lip Scrub | Cosmetics | Sugar lip scrub origami jar | Rotary locking ribs | Coated virgin board 300 gsm |
| 169 | Hex Petal Perfume Coffret | Perfume | Eau de Toilette seasonal floral box | 6-flap blossom opening | Heavyweight SBS 350 gsm |
| 170 | Iris Flower Tea Caddy | Confectionery | Rare white tea silver needle carton | Airtight inner petal seal | Kraft/foil duplex 280 gsm |
| 171 | Twist-Lock Snack Cup | Confectionery | Roasted almond on-the-go snack cup | Pinch-lock rim fold | PE-free aqueous barrier 250 gsm |
| 172 | Blooming Lotus Candle Box | Luxury Gifts | Soy candle unboxing floral platform | Base petals drop outward | Thick folding boxboard 380 gsm |
| 173 | Pinwheel Bath Salt Box | Cosmetics | Mineral bath crystals pourable carton | Corner-pour twist spout | Moisture-barrier kraft 300 gsm |
| 174 | Spiral Neck Flacon Box | Perfume | Slender perfume flacon upright carton | Spiral folding lock collar | SBS board 320 gsm |
| 175 | 8-Point Rosette Gift Box | Luxury Gifts | Silk tie & pocket square luxury set | Rosette center anchor | Premium textured card 350 gsm |
| 176 | Windmill Cookie Pouch | Confectionery | Gingerbread artisan single cookie pouch | Four-wing windmill tuck | Food-grade greaseproof 220 gsm |
| 177 | Radial Twist Coffee Pod Box| Eco-Minimalism | 10-count compostable espresso pod carton| Gravity-fed twist aperture | Recycled newsprint board 300 gsm |
| 178 | Iris Diamond Pendant Box | Luxury Gifts | Solitaire diamond pendant showcase box | Central dial iris unveil | Hard rigid board + velvet 400 gsm |
| 179 | Helical Spout Cream Box | Cosmetics | Body lotion refillable pouch support shell| Helical spout interlock | Stiff kraft cartonboard 350 gsm |
| 180 | Rotary Apex Blossom Box | Perfume | Mini fragrance discovery 3-pack | Blossom petal crown | Metallic art paper 300 gsm |

---

### Family 4: Interlocking, Friction-Fit & Zero-Glue Structures (Applications 181–240)
*Geometric Definition*: Single-sheet paperboard layouts erected entirely via tongue-and-slot, tab-and-mortise, rollover hollow walls, and friction detents, requiring zero hot-melt or chemical adhesives.
*Kinematic Behavior*: Elastic deformation of locking tabs followed by snap-fit retention; score allowances $K \cdot t$ compensate for board caliper $t \in [0.3\text{mm}, 2.0\text{mm}]$.

| ID | Geometric Topology | Industry Vertical | Application Description | Closure / Interlock | Substrate & Caliper |
|:---|:---|:---|:---|:---|:---|
| 181 | Double-Wall Rollover Tray | Eco-Minimalism | Zero-glue luxury shipping insert tray | Walker-lock foot tabs into base| SBS 350 gsm (0.45mm) |
| 182 | Self-Locking Clamshell Mailer| Eco-Minimalism | E-commerce returnable carton box | Ear-lock rollover tuck flap | E-flute corrugated 1.5mm |
| 183 | Friction-Fit Sliding Matchbox | Cosmetics | Dual lipstick drawer & sleeve set | Single-sheet folded friction tray| FBB 300 gsm (0.38mm) |
| 184 | Snap-Lock Bottom Box | Confectionery | Praline ballotin quick-assembly box | Automatic 1-2-3 snap bottom | Food-grade kraft 280 gsm |
| 185 | Simplex Fold-Over Corner Tray| Luxury Gifts | Fine stationery correspondence box | 4-corner diagonal friction web | Stiff greyboard 400 gsm |
| 186 | Interlocking Cross Carton | Perfume | Minimalist solid fragrance travel box | 4-way cross interlocking flap | Heavy unbleached kraft 350 gsm |
| 187 | Tab-and-Slit Hexagonal Box | Cosmetics | Hexagonal bath bomb zero-plastic carton | Dovetail tab and mortise slit | Recycled chipboard 300 gsm |
| 188 | Rollover Hollow-Wall Lid | Luxury Gifts | Rigid-look presentation box telescope lid | Beveled 45° corner locks | Cast-coated art card 380 gsm |
| 189 | Crash-Lock Gable Carrier | Confectionery | Artisanal bakery sourdough loaf tote | Self-locking bottom + handle | Heavy kraft 350 gsm |
| 190 | Wedge Friction Envelope | Cosmetics | Single sheet mask ultra-slim envelope | Curved tongue & slit lock | Uncoated kraft 240 gsm |
| 191 | Interlocking T-Slot Mailer | Eco-Minimalism | Plastic-free apparel subscription pack | Dual T-slot security tabs | Micro-flute corrugated 1.2mm |
| 192 | Double-Wall Gusset Tray | Perfume | Fragrance sample discovery set tray | Web corner zero-leak folds | White lined chipboard 320 gsm |
| 193 | Zero-Glue Hex Flacon Carrier | Perfume | Single perfume bottle cradle with carry ring| Base snap lock + collar grip | Virgin SBS 380 gsm |
| 194 | Multi-Slot Partition Tray | Confectionery | 9-piece artisan chocolate divider grid | Integrated folded partitions | Food-safe folding card 260 gsm |
| 195 | Self-Closing Pillow Box | Cosmetics | Eyelash curler ergonomic retail pack | Curved score self-tension ends | Clear-lacquered SBS 300 gsm |
| 196 | Reverse Tuck-End Carton | Cosmetics | Mascara tube standard retail carton | Friction dust flap with detent | FBB 280 gsm (0.35mm) |
| 197 | Friction-Grip Tube Box | Perfume | Roll-on fragrance oil slim rectangular carton| Tongue-in-groove side seam | Rigid kraft 320 gsm |
| 198 | Triangular Interlocking Tube | Confectionery | Toblerone-style chocolate prism carton | Hook-and-eye fold latch | Food-approved card 280 gsm |
| 199 | Rollover Channeled Tray | Luxury Gifts | Fountain pen desk organizer display | Channel-folded velvet cradle | Dense fiberboard 450 gsm |
| 200 | Snap-Together Hex Caddy | Eco-Minimalism | Organic seed packet multi-compartment holder| Central interlocking spine | 100% recycled kraft 320 gsm |
| 201 | Tongue-and-Eyelet Ballot | Confectionery | Single marzipan figurine favor box | Interlocking leaf-shaped tabs | Pearlescent board 250 gsm |
| 202 | Zero-Glue Bottle Pedestal | Perfume | Heavy glass flacon in-box shock pedestal | Folded box-beam suspension | Virgin kraft 400 gsm |
| 203 | Double-Tuck End Carton | Cosmetics | Day moisturiser glass jar outer carton | Pinhole friction lock tucks | SBS 350 gsm (0.44mm) |
| 204 | Self-Erecting Hexagonal Box | Luxury Gifts | Silk bow tie commemorative hexagonal box | Interlocking bottom petals | High-grade art board 350 gsm |
| 205 | Slit-Lock Gable Box | Confectionery | Wedding favor confectionery mini caddy | Interlocking roof ridge handle | Textured linen card 260 gsm |
| 206 | Clamshell Burger Box Fold | Confectionery | Warm brioche pastry takeaway clamshell | 4-point rollover locking tabs| Greaseproof unbleached 300 gsm |
| 207 | Interlocking Triangular Mailer| Eco-Minimalism | Rolled blueprint & silk scarf mailing tube | End-cap friction star locks | Heavy rigid kraft 420 gsm |
| 208 | Roll-End Tuck-Top (RETT) Box | Eco-Minimalism | Premium skincare e-commerce unboxing box | Front roll-end cherry locks | E-flute kraft corrugated 1.5mm |
| 209 | Dovetail Joint Paperboard Box| Luxury Gifts | Fine art watercolor pan travel case | Precision dovetail corner tabs| Stiff bookbinder board 500 gsm |
| 210 | Zero-Glue Tube Dispenser | Cosmetics | Cotton round makeup remover dispenser | Gravity-feed bottom slot | Recycled folding box 320 gsm |
| 211 | Self-Locking Octagon Box | Confectionery | Seasonal butter toffee sharing container | Alternating hook-tab lid | Food-safe SBS 300 gsm |
| 212 | Slotted Partition Wine Box | Eco-Minimalism | 3-bottle organic wine courier carton | Interlocking cross-grid | Double-wall B/C flute 4.0mm |
| 213 | Rollover Beveled Tray | Luxury Gifts | Swiss chronometer leather strap tray | 45° beveled rollover walls | Matte soft-touch SBS 380 gsm |
| 214 | Self-Tensioning Band Sleeve | Perfume | Discovery coffret outer belly band | Elastic friction paper clasp | Uncoated tactile paper 220 gsm |
| 215 | Interlocking Star Base Box | Cosmetics | Body scrub glass jar stable base carton | Star-folded interlocking floor | Heavy SBS 350 gsm |
| 216 | Dual-Flap Friction Wallet | Cosmetics | Disposable beauty blender dual wallet | Snap-crease side edges | Virgin SBS 260 gsm |
| 217 | Snap-In Blister Replacement | Eco-Minimalism | Razor handle & 4 blades zero-plastic tray | Integrated die-cut paper grips| Unbleached molded board 1.0mm |
| 218 | Zero-Glue Hexagon Mailer | Eco-Minimalism | Cylindrical candle glass courier mailer | Hexagonal crush-zone collar | B-flute corrugated 2.5mm |
| 219 | Fold-Over Flange Box | Confectionery | Artisanal jelly fruit slices luxury box | Double-flange perimeter lock | Food-grade SBS 300 gsm |
| 220 | Tongue-in-Slit Matchbox Sleeve| Luxury Gifts | Solid silver money clip presentation sleeve | Integrated stop-tab | Textured card 320 gsm |
| 221 | Self-Centering Bottle Insert | Perfume | Universal perfume flacon shock mount | Four-corner cantilever folds | Stiff kraft 350 gsm |
| 222 | Four-Corner Lock Tray | Confectionery | Pastry shop counter display tray | Hook-and-corner corner tabs | Coated duplex board 300 gsm |
| 223 | Interlocking Diamond Envelope| Luxury Gifts | Diamond certificate & appraisal envelope | Diamond flap tab into slit | Parchment-finish card 250 gsm |
| 224 | Zero-Glue Drawer System | Cosmetics | 3-tier modular eyeshadow palette stack | Intermeshing drawer runners | Heavyweight SBS 400 gsm |
| 225 | Tuck-Fold Sachet Carrier | Confectionery | Artisan hot chocolate spice blend pouch | Fold-and-tuck envelope seal | Barrier-treated kraft 240 gsm |
| 226 | Single-Sheet Gable Tote | Confectionery | Handcrafted cupcakes duo tote | Interlocking handle slit | Food-safe white card 320 gsm |
| 227 | Snap-Fit Compact Shell | Cosmetics | Mineral bronzer pressed powder paper compact| Die-cut snap detent catch | Hard greyboard 450 gsm |
| 228 | Rollover Cushion Mailer | Eco-Minimalism | Smartwatch accessories e-commerce mailer | Internal rollover buffer | E-flute corrugated 1.5mm |
| 229 | Double-Hook Tuck Box | Perfume | Heavy glass diffuser secondary packaging | Dual-hook reinforced base | Rigid unbleached board 380 gsm |
| 230 | Interlocking Leaf Pouch | Eco-Minimalism | Organic herbal bath infusion envelope | Dual leaf-shaped closure | Hemp-cellulose card 220 gsm |
| 231 | Self-Locking Pop-Up Plinth | Luxury Gifts | Commemorative gold bullion desk plinth | Auto-erect internal strut | Linen-embossed board 400 gsm |
| 232 | Slotted Hexagonal Tube | Confectionery | Gourmet grissini breadstick tall carton | Interlocking base star | Kraft board 300 gsm |
| 233 | Zero-Glue Ampoule Carrier | Cosmetics | 7-day concentrated booster ampoule rack | Rollover staircase divider | Virgin SBS 320 gsm |
| 234 | Pinch-Lock Pouch | Confectionery | Single chocolate truffle impulse pack | Pre-scored spring pinch top | Metallic card 250 gsm |
| 235 | Interlocking Pentagonal Tube | Perfume | Slender pocket fragrance spray carton | Pentagonal hook-tab closure | Stiff SBS 300 gsm |
| 236 | Clasp-Lock Envelope Box | Luxury Gifts | Silk neckerchief flat-pack gift box | Interlocking origami clasp | Heavy art card 320 gsm |
| 237 | Friction-Fold Eyewear Case | Eco-Minimalism | Fold-flat sunglasses protective travel case | Magnetic paperboard triangle | Recycled fiberboard 400 gsm |
| 238 | Double-Locking Cake Tray | Confectionery | Gateau presentation base with lift wings | Fold-up handle grips | Grease-resistant SBS 350 gsm |
| 239 | Modular Snap-Together Bin | Eco-Minimalism | Cosmetics vanity counter recyclable organizer| Dovetail side connectors | Heavy kraft board 450 gsm |
| 240 | Zero-Glue Crash-Lock Shipper | Eco-Minimalism | High-volume luxury e-commerce shipping box| Automatic self-locking bottom | Microflute corrugated 1.8mm |

---

### Family 5: Modular, Nested & Kinetic Reveal Mechanisms (Applications 241–300+)
*Geometric Definition*: Multi-panel kinematic assemblies incorporating linked folding mechanisms, pop-up plinths, sliding cantilever arms, and expanding multi-stage reveal chambers.
*Kinematic Behavior*: Planar linkage chains (4-bar and 6-bar equivalent paper mechanisms); deployment velocity and sequence strictly governed by crease geometry.

| ID | Geometric Topology | Industry Vertical | Application Description | Closure / Interlock | Substrate & Caliper |
|:---|:---|:---|:---|:---|:---|
| 241 | Exploding Memory Box | Luxury Gifts | Multi-layer milestone anniversary reveal box | 4-stage cascading drop walls| Heavy SBS 350 gsm + Art paper |
| 242 | Cantilevered Multi-Tier Tray | Cosmetics | Professional makeup artist tiered vanity box | Linked 4-bar paper arms | Rigid greyboard 1.5mm + card |
| 243 | Pop-Up Pedestal Vault | Perfume | Grand reveal coffret, lifts bottle on opening | Kinematic lifting plinth | Bookbinding greyboard 2.0mm |
| 244 | Sliding Dual-Wing Coffret | Luxury Gifts | Haute horlogerie dual-drawer reveal suite | Synchronized rack fold | Velvet-wrapped board 400 gsm |
| 245 | Kaleidoscope Hexagonal Prism| Confectionery | 6-compartment rotating praline carousel | Center dowel rotation | Food-safe rigid card 350 gsm |
| 246 | Accordion Pull-Out Sampler | Cosmetics | 10-shade lipstick sample fan display | Ribbon-pull accordion track | Coated 2-side SBS 300 gsm |
| 247 | Origami Flower Pop-Up Plinth| Perfume | Fragrance flacon sits atop blooming flower | Interlinked petal linkages | Pearlescent art paper 250 gsm |
| 248 | Nested Russian Doll Prisms | Luxury Gifts | Russian doll nested 3-tier jewelry boxes | Friction-fit step sizes | Dense virgin kraft 350 gsm |
| 249 | Expanding Fan Chocolate Box | Confectionery | Fan-shaped 180° opening bonbon assortment | Semi-circular fan fold | Gold foil-stamped board 300 gsm |
| 250 | Dual-Pivot Wing Compact | Cosmetics | Eyeshadow duo opening like butterfly wings | Linked pivot pinholes | Recycled rigid board 400 gsm |
| 251 | Telescopic Hexagonal Tower | Perfume | Limited-edition 3-fragrance modular stack | Telescoping friction collars | Rigid paper tubes + wrap |
| 252 | Pop-Up Architectural Diorama| Luxury Gifts | Heritage boutique perfume VIP invitation | Multi-layer laser pop-up | High-precision art paper 220 gsm |
| 253 | Sliding Spiral Compartment | Confectionery | Gourmet marzipan spiral drawer caddy | Helical guide tracks | Stiff SBS card 350 gsm |
| 254 | Kinematic Theater Box | Cosmetics | Red-carpet cosmetics palette stage reveal | Curtain-fold opening linkage | Matte laminated SBS 380 gsm |
| 255 | Modular Hexagonal Honeycomb | Eco-Minimalism | Zero-plastic modular spice or cosmetic rack | Interlocking clip slots | Recycled testliner 350 gsm |
| 256 | Kinetic Origami Diamond Box | Luxury Gifts | Pop-up diamond facet ring presentation box | Spring-creased facet hinge | Cast-coated duplex 320 gsm |
| 257 | Parallelogram Linkage Tray | Cosmetics | 3-tier false eyelash professional kit | Parallel motion fold arms | Virgin SBS 300 gsm |
| 258 | Rotating Hexagonal Carousel | Confectionery | Single-origin bean-to-bar chocolate library | Center pivot carousel base | Stiff cardboard 400 gsm |
| 259 | Push-Activated Elevator Box | Perfume | Bottle rises automatically when lid is pulled | Counterweighted ribbon pull | Greyboard wrapped in silk |
| 260 | Origami Book Unboxing Box | Luxury Gifts | Fine fountain pen storybook presentation | Magnetic book spine clasp | Heavy buckram over board |
| 261 | Nested Hexagonal Coffret | Cosmetics | Complete morning skincare routine 4-step box| Stepped concentric trays | SBS board 350 gsm |
| 262 | Expanding Accordion Easel | Confectionery | Countertop retail display for praline bars | Auto-erecting easel strut | E-flute corrugated 1.5mm |
| 263 | Folding Cube Magic Box | Luxury Gifts | Yoshimoto cube-inspired fidget gift box | Continuous hinge joints | Synthetic tear-proof card 240 gsm |
| 264 | Kinetic Wing Perfume Case | Perfume | Flacon reveals with opening flanking doors | Synchronized cam flaps | Rigid paperboard 450 gsm |
| 265 | Pop-Up Chandelier Box | Luxury Gifts | Diamond chandelier earring luxury vault | Suspended pop-up wire/paper| High-finish SBS 380 gsm |
| 266 | Multi-Tier Macaron Pyramid | Confectionery | 4-tier wedding macaron tower, packs flat | Concentric snap rings | Food-approved virgin FBB 300 gsm |
| 267 | Dual-Action Slide & Tilt Pod | Cosmetics | Cushion foundation angled unboxing box | Cam-tilt bottom ramp | Heavy coated card 320 gsm |
| 268 | Modular Triangular Trio | Eco-Minimalism | Solid shampoo, conditioner, body wash set | Interlocking triangular bands| Unbleached bamboo pulp 300 gsm |
| 269 | Iris Pop-Up Center Plinth | Perfume | Scent bottle rises through blooming petals | Linked radial petals + lift | Pearlescent card 300 gsm |
| 270 | Sliding T-Bar Reveal Box | Luxury Gifts | Luxury silk tie & cufflinks dual chamber | Interlinked T-slide drawer | Matte black chipboard 400 gsm |
| 271 | Kinetic Diamond Staircase | Confectionery | 7-day culinary spice or confection countdown| Stepped diagonal slide | Reinforced kraft 320 gsm |
| 272 | Origami Umbrella Candy Box | Confectionery | Festive bonbon parasol presentation box | Radial rib umbrella mechanism| Coated card 260 gsm |
| 273 | Telescopic Lift Serum Box | Cosmetics | High-potency active serum launch box | Dual telescoping stage | High-density paperboard 380 gsm |
| 274 | Kinetic Accordion Wallet | Luxury Gifts | Multi-card luxury VIP club membership kit | Expanding 6-compartment fan | Fine bookbinding paper 240 gsm |
| 275 | Butterfly Wings Reveal Box | Perfume | Niche perfume flacon with expanding wings | Linked diagonal fold wings | Heavy art board 400 gsm |
| 276 | Folding Octagon Carousel | Confectionery | 8-tea assortment rotating tasting box | Central pivot locking rivet | Food-safe unbleached 320 gsm |
| 277 | Kinematic Pop-Up Compact | Cosmetics | Pressed powder with auto-elevating mirror | Angled paper hinge arm | Stiff greyboard 400 gsm |
| 278 | Nested Square Bipyramids | Luxury Gifts | 3-piece nested heirloom pendant suite | Concentric facet friction | Textured linen card 320 gsm |
| 279 | Origami Stage Light Box | Perfume | Fragrance bottle highlighted by angled facets| Light-funneling facet geometry| Metallic mirror card 350 gsm |
| 280 | Sliding Hex Star Box | Confectionery | 6-compartment star chocolate assortment | Radial sliding drawers | Food-grade SBS 300 gsm |
| 281 | Kinetic Facet Clamshell | Cosmetics | High-end makeup brush cleaning & case | Self-opening facet spine | Poly-coated kraft 300 gsm |
| 282 | Pop-Up Gemstone Monolith | Luxury Gifts | Loose uncut sapphire presentation plinth | Precision pop-up geometry | Heavy black card 380 gsm |
| 283 | Concentric Folding Cylinders | Perfume | 3-piece fragrance layering discovery set | Nested cylinder sleeves | Spiral wound board 1.2mm |
| 284 | Kinetic Accordion Display | Confectionery | Chocolate tablet 5-origin tasting kit | Fold-out zig-zag display stand| Recycled board 320 gsm |
| 285 | Double-Door Theater Coffret | Luxury Gifts | Rare vintage cognac mini flacon showcase | Magnetic theater double doors| Rigid paperboard 2.5mm |
| 286 | Modular Honeycomb Wine Rack | Eco-Minimalism | 6-bottle flat-pack shipping & cellar rack | Interlocking slot grid | Double-wall BC flute 6.0mm |
| 287 | Kinetic Twist Dispenser | Cosmetics | Daily anti-aging capsule mechanical hopper | Rotary gravity feed chute | Stiff folding boxboard 350 gsm |
| 288 | Multi-Stage Secret Box | Luxury Gifts | Puzzle-box style jewelry unboxing experience | 3-step concealed slide locks | Heavyweight card 420 gsm |
| 289 | Pop-Up Flower Bouquet Box | Confectionery | Edible wafer flower confection reveal | 3D paper bouquet mechanism | Food-contact art card 240 gsm |
| 290 | Cascading Stepped Drawers | Cosmetics | 12-day luxury advent beauty calendar | Pull-ribbon cascading drawers| Rigid greyboard + art paper |
| 291 | Kinetic Faceted Collar Box | Perfume | Flacon with faceted collar that opens wide | Perimeter facet linkage | Soft-touch SBS 350 gsm |
| 292 | Origami Lantern Gift Caddy | Luxury Gifts | Festive tea light or aroma diffuser box | Expanding lantern ribs | Heat-resistant paperboard 280 gsm |
| 293 | Expanding Macaron Carousel | Confectionery | 16-piece wedding macaron presentation | Circular expanding fan | Virgin food board 300 gsm |
| 294 | Dual-Axis Hinged Compact | Cosmetics | Cream-to-powder multi-palette case | Two-axis paper living hinges | Dense recycled board 450 gsm |
| 295 | Kinetic Octagonal Pavilion | Luxury Gifts | High jewelry tiara or necklace pavilion | Hex/octagonal opening walls | Satin-covered rigid board |
| 296 | Pop-Up Flacon Suspension | Perfume | Drop-tested perfume carton with kinetic core | Suspended paper spring net | High-tensile kraft 300 gsm |
| 297 | Modular Interlocking Cubes | Eco-Minimalism | Zero-glue modular shelf display boxes | Corner dovetail paper keys | Heavy duty corrugated 2.0mm |
| 298 | Kinetic Sliding Diamond Box | Luxury Gifts | Diamond bracelet sliding reveal case | Angled cam-action drawer | Virgin SBS 400 gsm |
| 299 | Accordion Pop-Up Coffret | Perfume | 4-fragrance wardrobe discovery kit | Linked pop-up pedestals | Rigid folding card 380 gsm |
| 300 | Triangulated Kinetic Vault | Luxury Gifts | Master watchmaker annual timepiece vault | 6-facet synchronized bloom | Carbon-black virgin board 500 gsm |
| 301 | Modular Bento Feast Box | Confectionery | Multi-course Japanese wagashi dessert box | Self-locking nested partitions| Food-contact unbleached 350 gsm |
| 302 | Blooming Rose Gold Coffret | Cosmetics | Limited holiday highlighter & brush vault | Multi-layer metallic rose bloom| Laminated luxury card 400 gsm |
| 303 | Kinetic Helical Wine Shipper| Eco-Minimalism | Single-bottle zero-plastic impact shipper | Internal helical paper spring | E/F flute corrugated 2.2mm |
| 304 | Pop-Up Jewel Star Monolith | Luxury Gifts | Fine jewelry solitaire pendant star reveal | Integrated 3D star pop-up | Velvet-flocked SBS 380 gsm |
| 305 | Kinetic Sliding Iris Vault | Perfume | Haute parfumerie crystal flacon master box | Integrated sliding iris canopy| Stiff bookbinder greyboard 2.0mm |

---

### 2. Cross-Family Design Selection Matrix

When selecting an origami packaging family for a specific engineering requirement, evaluate the following performance criteria:

```
Family                         Assembly Speed   Volumetric Eff.   Impact Absorpt.   Tactile Wow   Plastic-Free Score
1. Polyhedral & Faceted          Moderate           High               High             Very High        100%
2. Tessellated / Kinetic         Fast (Auto)        Very High          Maximum          High             100%
3. Radial & Iris Twisting        Moderate           High               Moderate         Maximum          100%
4. Zero-Glue Interlocking        Ultra-Fast         Maximum            High             High             100%
5. Modular & Kinetic Reveal      Slow (Luxury)      Moderate           Moderate         Maximum          95–100%
```

---

### 3. CAD Dieline Layering & Geometric Feasibility Rules

For automated laser die cutting and CNC sample table routing (Zünd, Kongsberg), all 300+ catalog designs must enforce strict CAD layer segregation:

1. **CUT (`#FF0000`)**: Continuous peripheral through-cut knife lines. Must be closed loops or terminate at outer sheet edges.
2. **CREASE (`#00FF00`, dashed `4,4`)**: Mountain and valley score lines. Crease rule width $w_r$ and channel depth $d_c$ must match paperboard caliper:
   $$w_r \approx t, \quad d_c \approx 1.5 t$$
3. **PERFORATE (`#0000FF`, dotted `2,2`)**: Alternating cut/skip rule (e.g., $2.0\text{mm}$ cut, $2.0\text{mm}$ tie) for tear-away safety bands and high-angle stress relief folds.
4. **GLUE / INTERLOCK (`#FF00FF`, cross-hatch)**: Mechanical locking tab insertion zones or adhesive application corridors.

---

## Failure Modes (Mandatory)
1. **Multi-Crease Vertex Jamming**: Concentrating more than 4 crease lines at a single vertex without relief cutouts; causes paperboard fiber compression failure, delamination, and mechanical locking that prevents proper folding.
2. **Grain Direction Misalignment**: Placing critical 180° rollover creases parallel to paper grain instead of perpendicular; causes severe fiber cracking, jagged tears, and premature hinge failure under repeated opening cycles.
3. **Uncompensated Caliper Interference**: Designing zero-glue interlocking tabs with zero tolerance ($t=0$); causes tabs to bow, bind, or tear during insertion as board caliper ($0.3-1.5\text{mm}$) crowds internal cavity volume.
4. **Rotational Iris Over-Torque**: Under-sizing the radial clearance in Family 3 twist closures; causes excessive opening torque that shears the paperboard driving arms before the aperture unlocks.
5. **Springback-Induced Unlocking**: Relying on friction detents without adequate tab lead-in chamfers ($15^\circ-30^\circ$) or retention notches; causes the package to spring open spontaneously under board elastic recovery forces.
