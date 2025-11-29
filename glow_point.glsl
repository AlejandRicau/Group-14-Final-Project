// glow_point.glsl
uniform vec2 u_points[100];
uniform int u_point_count;
uniform vec3 u_color;

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec3 finalColor = vec3(0.0);

    for (int i = 0; i < u_point_count; i++) {
        vec2 pos = fragCoord.xy - u_points[i];

        // --- TUNING FOR LARGER ORB ---
        // Changed 0.1 -> 0.06 (Makes the ball larger)
        // Kept numerator 0.5 (Keeps brightness low)
        float dist = 0.5 / (length(pos) * 0.06 + 0.1);

        // Standard falloff
        dist = pow(dist, 1.5);

        finalColor += u_color * dist;
    }

    fragColor = vec4(finalColor, 1.0);
}