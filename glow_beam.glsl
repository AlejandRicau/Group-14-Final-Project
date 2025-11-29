// glow_beam.glsl
// Used for: Base Tower Bullets (Solid Steam Jet)

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

        float d = distanceToLineSegment(start, end, fragCoord.xy);

        // --- SOLID STEAM LOOK ---
        // 5.0 / (d + 5.0) gives a nice thick core
        float intensity = 5.0 / (d + 5.0);

        // Power 2.0 makes the edge soft but defined
        intensity = pow(intensity, 2.0);

        finalColor += u_color * intensity;
    }

    fragColor = vec4(finalColor, 1.0);
}