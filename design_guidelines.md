# Modern RPG Game UI Design Guidelines

## Design Approach
**Reference-Based**: Drawing inspiration from AAA RPG games (Cyberpunk 2077, Diablo IV, Path of Exile) combined with modern gaming dashboard aesthetics. Focus on premium, adult-oriented gaming experience with futuristic/cyberpunk undertones.

---

## Typography System

**Primary Font**: "Orbitron" or "Rajdhana" (Google Fonts) - geometric, tech-forward
**Secondary Font**: "Inter" or "Roboto Condensed" - clean readability for body text

**Hierarchy:**
- Hero/Display: 48-72px, bold, uppercase, letter-spacing +2px
- Section Headers: 32-40px, semibold, uppercase
- Card Titles: 20-24px, medium
- Body Text: 14-16px, regular, +0.5px letter-spacing
- Labels/Meta: 12-14px, uppercase, medium, +1px letter-spacing

---

## Layout System

**Spacing Units**: Tailwind 2, 4, 6, 8, 12, 16 units
**Container**: max-w-7xl with px-4 to px-8
**Grid System**: Primarily asymmetric layouts with angled card grids

**Structural Elements:**
- Angled containers: -skew-y-1 or skew-y-1 on parent, reverse on content
- Clipped corners: clip-path polygons for octagonal/hexagonal panels
- Layered depth: Multiple z-index levels with backdrop shadows

---

## Component Library

### Hero Section
**Full viewport height (100vh)** with parallax-ready background image overlay
- Dark gradient overlay (90% opacity black to transparent)
- Title with neon text glow effect
- CTA buttons with blur background (backdrop-blur-md, bg-black/30)
- Stats bar underneath: Player count, servers, latest update info
- Diagonal accent lines framing content

### Navigation
**Fixed header** with blur background (backdrop-blur-xl, bg-black/80)
- Logo left, navigation center, user profile/CTA right
- Hover states: Neon underline animations
- Mobile: Slide-in panel with same angled aesthetic

### Feature/Ability Cards
**Asymmetric grid** (2-3 columns on desktop)
- Angled card containers with skew transforms
- Dark backgrounds (bg-gray-900/50) with 1px neon borders
- Icon/image area with gradient overlays
- Title, description, stats/attributes
- Hover: Slight scale + border glow intensification

### Character/Item Panels
**Layered information displays**
- Primary panel: Large character/item visual with dark vignette
- Side panels: Stats, abilities, equipment slots in smaller angled sections
- Progress bars with neon gradient fills
- Tooltips with glass-morphism effect

### Data Tables/Leaderboards
**Striped rows** with alternating dark grays
- Header row with neon accent bottom border
- Rank indicators with badge styling
- Hover: Subtle neon glow on entire row

### Modals/Overlays
**Full-screen takeover** with heavy blur background
- Central content panel at 80% max-width
- Angled corners or octagonal shaping
- Close button: Neon "X" in corner
- Content: Scrollable with custom scrollbar styling

### Buttons
**Primary**: Solid dark background with neon border, uppercase text
**Secondary**: Outline only with neon color
**Ghost**: Text-only with neon color
- All buttons: Subtle glow effect on hover, +2px bottom border for depth

### Forms
**Glass-morphism inputs**: backdrop-blur-sm with dark translucent backgrounds
- Neon focus rings (cyan/lime)
- Label: Uppercase, small, positioned above
- Error states: Red neon glow
- Checkboxes/radios: Custom styled with angled designs

---

## Visual Effects

**Depth Techniques:**
- Drop shadows: Multiple layered shadows (sm, md, lg in dark gray/black)
- Inner shadows for recessed panels
- Border highlights: 1px neon on top/left, darker on bottom/right

**Glow Effects:**
- Text glows: text-shadow with neon color blur
- Border glows: box-shadow with accent color spread
- Interactive elements pulse with subtle glow animation

**Textures:**
- Subtle noise overlay on backgrounds (10% opacity)
- Diagonal scanline patterns on panels (very subtle)
- Grid patterns for tech aesthetic in backgrounds

---

## Images

**Hero Background**: High-resolution RPG game scene or character artwork
- Placement: Full-screen background
- Treatment: Dark gradient overlay, subtle parallax

**Feature Section Images**: Character classes, abilities, or game environments
- Placement: Within angled card components
- Treatment: Gradient vignettes, neon accent borders

**Gallery/Screenshots**: In-game footage or concept art
- Placement: Masonry grid or horizontal scroll carousel
- Treatment: Hover zoom, border glow effects

**Avatar/Profile Images**: Player characters or user profiles
- Placement: Navigation, leaderboards, profile sections
- Treatment: Hexagonal or octagonal clip-path masks, neon borders

---

## Key Design Principles

1. **Depth over Flatness**: Always layer elements with shadows and glows
2. **Angles over Curves**: Use skewed containers, clipped corners, diagonal accents
3. **Neon Sparingly**: Use cyan/lime for interactive elements, calls-to-action, highlights only
4. **Dark Foundation**: Black (rgb(0,0,0)) and dark grays (rgb(15,15,15) to rgb(30,30,30))
5. **Tech Aesthetic**: Grid overlays, scanlines, geometric patterns as background details
6. **Information Density**: Display stats, numbers, progress bars prominently - gamers expect data-rich interfaces