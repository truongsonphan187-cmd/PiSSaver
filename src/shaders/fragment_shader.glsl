#version 330 core
out vec4 FragColor;

uniform vec2 u_resolution;
uniform vec2 u_image_size;
uniform sampler2D u_texture;
uniform float u_time;
uniform float u_led_size;
uniform float u_spacing_ratio;
uniform float u_wave_speed;
uniform float u_negative_dim;

void main() {
    // Pixel coordinates with origin (0,0) at the top-left of the screen
    vec2 frag_coord = vec2(gl_FragCoord.x, u_resolution.y - gl_FragCoord.y);

    // Compute aspect ratios for screen and image
    float screen_ar = u_resolution.x / u_resolution.y;
    float image_ar = u_image_size.x / u_image_size.y;
    float ar_ratio = screen_ar / image_ar;
    
    vec2 draw_size;
    vec2 draw_offset;
    
    // Smart Adaptive Crop/Fit:
    // Only crop/fill when aspect ratios are close (e.g. 16:9 on 16:10 or vice-versa) for 100% borderless display.
    // For 1:1 square artwork (e.g. MJ Invincible) or 4:3, use Aspect Fit centered to avoid clipping the subject.
    bool should_crop_fill = (ar_ratio >= 0.85 && ar_ratio <= 1.18);

    if (should_crop_fill) {
        // Center-Crop / Fill full screen
        if (screen_ar > image_ar) {
            draw_size = vec2(u_resolution.x, u_resolution.x / image_ar);
            draw_offset = vec2(0.0, (u_resolution.y - draw_size.y) * 0.5);
        } else {
            draw_size = vec2(u_resolution.y * image_ar, u_resolution.y);
            draw_offset = vec2((u_resolution.x - draw_size.x) * 0.5, 0.0);
        }
    } else {
        // Aspect Fit centered with black LED grid margin
        if (screen_ar > image_ar) {
            draw_size = vec2(u_resolution.y * image_ar, u_resolution.y);
            draw_offset = vec2((u_resolution.x - draw_size.x) * 0.5, 0.0);
        } else {
            draw_size = vec2(u_resolution.x, u_resolution.x / image_ar);
            draw_offset = vec2(0.0, (u_resolution.y - draw_size.y) * 0.5);
        }
    }

    // Determine LED matrix grid cell
    vec2 cell_idx = floor(frag_coord / u_led_size);
    vec2 cell_center = (cell_idx + 0.5) * u_led_size;
    float radius = (u_led_size * 0.5) * u_spacing_ratio;
    float dist = length(frag_coord - cell_center);

    // Dark bezel color between LED dots
    vec3 bezel_color = vec3(0.035, 0.035, 0.04);

    // Check if cell is within the image bounds or outer padding
    bool is_outside = (cell_center.x < draw_offset.x || cell_center.x > draw_offset.x + draw_size.x ||
                       cell_center.y < draw_offset.y || cell_center.y > draw_offset.y + draw_size.y);

    vec3 base_color;
    if (is_outside) {
        // Outside area: uniform unlit LED dot
        base_color = vec3(0.015, 0.015, 0.02);
    } else {
        vec2 uv = (cell_center - draw_offset) / draw_size;
        uv = clamp(uv, 0.0, 1.0);
        base_color = texture(u_texture, uv).rgb;
    }

    // Majestic Ocean Swell wave effect (3x Wavelength):
    // Wavelength = 255.0 LED dots: creates an expansive, rolling tide across the entire screen.
    // Wave height maps directly to luminosity:
    // - Crest (positive): climbs up to ~115% luminosity for glistening peak highlight.
    // - Trough (negative): dips down to ~42% for deep 3D shadow while retaining vivid color.
    float wave_factor = 1.0;
    if (u_wave_speed > 0.001) {
        float wave_coord = cell_idx.x + cell_idx.y;
        float wavelength = 255.0; // 3x broader wavelength per user instruction
        float phase = (wave_coord / wavelength) * 6.2831853 - (u_time * u_wave_speed * 1.5);
        float s = sin(phase);

        if (s >= 0.0) {
            // Wave crest: smoothly boost to 115%
            float crest = smoothstep(0.0, 1.0, s);
            wave_factor = mix(1.0, 1.15, crest);
        } else {
            // Wave trough: smoothly dip to 42% for distinct depth
            float trough = smoothstep(0.0, -1.0, s);
            wave_factor = mix(1.0, 0.42, trough);
        }
    }

    // 3D spherical dome lens effect
    float norm_dist = clamp(dist / radius, 0.0, 1.0);
    float lens = 1.0 - 0.22 * norm_dist * norm_dist;
    
    // Specular glint on top-left of each LED bulb
    vec2 glint_pos = cell_center - vec2(radius * 0.28, radius * 0.28);
    float glint_dist = length(frag_coord - glint_pos);
    float glint = exp(-glint_dist * glint_dist / (radius * 0.28 * radius * 0.28)) * 0.12;

    vec3 dot_color = (base_color * wave_factor * lens) + vec3(glint);

    // Anti-aliasing on circular LED dot border
    float edge = 1.0 - smoothstep(radius - 0.75, radius + 0.25, dist);

    // Blend LED bulb color over bezel background
    vec3 final_color = mix(bezel_color, dot_color, edge);
    FragColor = vec4(final_color, 1.0);
}
