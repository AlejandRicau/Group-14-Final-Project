// projectile_glow.glsl

uniform vec2 u_points[100];
uniform int u_point_count;
uniform vec3 u_color;
uniform int u_shape; // 0 = Circle, 1 = Square

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    float total_brightness = 0.0;

    for (int i = 0; i < u_point_count; i++) {
        float dist = 0.0;

        if (u_shape == 1) {
            // --- SQUARE SHAPE (Box Distance) ---
            vec2 diff = abs(fragCoord.xy - u_points[i]);
            dist = max(diff.x, diff.y);
        } else {
            // --- CIRCLE SHAPE (Euclidean Distance) ---
            dist = distance(fragCoord.xy, u_points[i]);
        }

        // --- Intensity Calculation ---
        // We use a high exponent (2.5) to keep the glow "tight" and not fuzzy.

        float intensity = 1500.0;

        // Calculate brightness with falloff
        float brightness = intensity / (pow(dist, 2.5) + 1.0);

        // Clamp to prevent white-out
        brightness = min(brightness, 1.2);

        total_brightness += brightness;
    }

    vec3 final_col = u_color * total_brightness;
    fragColor = vec4(final_col, 1.0);
}