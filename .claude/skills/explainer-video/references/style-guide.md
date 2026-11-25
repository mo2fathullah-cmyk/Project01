# Style guide (from EP1, approved)
Frame 1080x1920, navy radial gradient (#17457A → #0C2B55 → #061631) + static grain (opacity .09).
Zones (y px): logo plate + series pill 48-136 · course tag 146 · headline 236 (Inter Display 800, 74px, cream #F3E9D2)
· stage 400-1150 (SVG 1080x750, flat shapes) · cards/formula 868-1144 · meters 1180-1430 · footnote 1438
· captions 1488-1668 (Inter 800, 50px, key word #F7A04B) · watermark "DrFath" top 1748 right 52.
Palette: orange #E07B39, highlight #F7A04B, teal #2E7D6B, sky #3FA9E0, gold #F2C14E, grey-blue #B8C7D9, paper #FFF7E6, ink #0B1F35, brown #8A5A2B.
Components in templates/episode.html: floating label pills (.lbl b/u/t) with dashed connectors, number cards (.card),
formula card (.fx with l1 formula / l2 terms revealed one by one / l3 result), 3 meters kWh·RM·CO2 (motif for calculation
episodes; omit for concept episodes), KEY POINT card (#key) + chip equation (#eq), Pause & Try (#quiz + 5 s ring + #ans), outro.
Live motion (fans, pulses, coins, clouds, countdown) is computed from t inside seek() so frames are deterministic.
