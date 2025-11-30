// vignette.glsl

uniform vec2 u_towers[100]; // Contains Towers + Goals + Spawns
uniform int u_tower_count;

void mainImage(out vec4 fragColor, in vec2 fragCoord) {

    // 1. Calculate Distance from Center
    vec2 uv = fragCoord.xy / iResolution.xy;

    // Fix aspect ratio so the "center clear zone" is round, not squished
    vec2 center_vec = uv - 0.5;
    center_vec.x *= iResolution.x / iResolution.y;
    float center_dist = length(center_vec);

    // 2. Base Darkness Gradient
    // Instead of a flat 0.95, we use a gradient.
    // Center (0.0 dist) -> 0.6 alpha (Dim)
    // Edge (0.7 dist)   -> 0.95 alpha (Dark)
    float base_darkness = 0.6 + smoothstep(0.2, 0.7, center_dist) * 0.35;

    float darkness = base_darkness;

    // 3. Dynamic Lighting (Punch holes)
    for (int i = 0; i < u_tower_count; i++) {
        float dist = distance(fragCoord.xy, u_towers[i]);

        // Light Radius ~180px
        float light = 1.0 - smoothstep(0.0, 180.0, dist);

        // Remove darkness
        darkness -= light * 1.2;
    }

    // 4. Clamp
    // Keep it between 0.0 (Clear) and 0.98 (Almost Pitch Black)
    darkness = clamp(darkness, 0.0, 0.98);

    fragColor = vec4(0.0, 0.0, 0.0, darkness);
}