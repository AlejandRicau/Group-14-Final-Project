// steam.glsl

// Inputs: Position (x, y) and Radius (z)
uniform vec3 u_puffs[100];
uniform int u_puff_count;

// Steam Color (White/Grey)
const vec3 cloud_color = vec3(0.9, 0.9, 0.95);

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    float total_density = 0.0;

    for (int i = 0; i < u_puff_count; i++) {
        vec2 puff_pos = u_puffs[i].xy;
        float radius = u_puffs[i].z;

        // Distance in pixels
        float dist = distance(fragCoord.xy, puff_pos);

        // Soft Cloud Shape
        // Smoothstep creates a nice fuzzy edge from 0.0 to radius
        float density = 1.0 - smoothstep(0.0, radius, dist);

        // Additive density
        total_density += density;
    }

    // Clamp density (max opacity 0.8 so it's slightly see-through)
    total_density = min(total_density, 0.8);

    // Output pre-multiplied alpha
    fragColor = vec4(cloud_color * total_density, total_density);
}