// glow_beam.glsl
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

        // --- TUNING FOR WIDER, SOFT BEAM ---
        // Numerator 5.0 / Denom + 5.0 gives a wider core than 3.0/4.0
        float intensity = 5.0 / (d + 5.0);

        // Exponent 1.8 (was 2.0) makes the "halo" larger/softer
        intensity = pow(intensity, 1.8);

        finalColor += u_color * intensity;
    }

    fragColor = vec4(finalColor, 1.0);
}