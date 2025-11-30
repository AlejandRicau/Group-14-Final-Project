// glow_laser.glsl

uniform vec4 u_lines[100];
uniform int u_line_count;
uniform vec3 u_color;

float distanceToLineSegment(vec2 startPoint, vec2 endPoint, vec2 testPoint)
{
    vec2 g = endPoint - startPoint;
    vec2 h = testPoint - startPoint;
    return length(h - g * clamp(dot(g, h) / dot(g,g), 0.0, 1.0));
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec3 finalColor = vec3(0.0);

    for (int i = 0; i < u_line_count; i++) {
        vec2 start = u_lines[i].xy;
        vec2 end = u_lines[i].zw;

        // 1. Calculate Distance (Shape)
        float d = distanceToLineSegment(start, end, fragCoord.xy);

        // --- TUNING FOR STEAM COLUMN ---
        // OLD: 3.0 / (d + 3.0) -> Thin Beam
        // NEW: 8.0 / (d + 8.0) -> Thick Column
        // Increasing these numbers makes the "hot core" wider.
        float intensity = 8.0 / (d + 8.0);

        // Lower power (1.5) makes the edges "fuzzier" (like smoke)
        intensity = pow(intensity, 1.5);

        // 2. Calculate Gradient (Fade)
        vec2 dir = end - start;
        float lenSq = dot(dir, dir);
        float t = 0.0;
        if (lenSq > 0.0) {
            t = clamp(dot(fragCoord.xy - start, dir) / lenSq, 0.0, 1.0);
        }

        // Fade Logic:
        float fade = mix(1.0, 0.0, t);
        intensity *= fade;

        finalColor += u_color * intensity;
    }

    fragColor = vec4(finalColor, 1.0);
}