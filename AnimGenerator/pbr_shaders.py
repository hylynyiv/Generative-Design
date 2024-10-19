from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

class Shader:
    def __init__(self):
        self.vertex_shader = """
        #version 120
        attribute vec3 aPos;
        attribute vec3 aNormal;
        varying vec3 FragPos;
        varying vec3 Normal;
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;
        uniform mat3 normalMatrix;
        void main()
        {
            FragPos = vec3(model * vec4(aPos, 1.0));
            Normal = normalMatrix * aNormal;
            gl_Position = projection * view * vec4(FragPos, 1.0);
        }
        """

        self.fragment_shader = """
        #version 120
        varying vec3 FragPos;
        varying vec3 Normal;

        uniform vec3 viewPos;
        uniform vec3 albedo;
        uniform float metallic;
        uniform float roughness;
        uniform float ao;

        const int MAX_LIGHTS = 10;
        uniform vec3 lightPos[MAX_LIGHTS];
        uniform vec3 lightColor[MAX_LIGHTS];
        uniform int numLights;

        const float PI = 3.14159265359;

        vec3 fresnelSchlick(float cosTheta, vec3 F0) {
            return F0 + (1.0 - F0) * pow(clamp(1.0 - cosTheta, 0.0, 1.0), 5.0);
        }

        float DistributionGGX(vec3 N, vec3 H, float roughness) {
            float a = roughness * roughness;
            float a2 = a * a;
            float NdotH = max(dot(N, H), 0.0);
            float NdotH2 = NdotH * NdotH;

            float num = a2;
            float denom = (NdotH2 * (a2 - 1.0) + 1.0);
            denom = PI * denom * denom;

            return num / max(denom, 0.0001);
        }

        float GeometrySchlickGGX(float NdotV, float roughness) {
            float r = (roughness + 1.0);
            float k = (r * r) / 8.0;
            return NdotV / (NdotV * (1.0 - k) + k);
        }

        float GeometrySmith(vec3 N, vec3 V, vec3 L, float roughness) {
            float NdotV = max(dot(N, V), 0.0);
            float NdotL = max(dot(N, L), 0.0);
            float ggx2 = GeometrySchlickGGX(NdotV, roughness);
            float ggx1 = GeometrySchlickGGX(NdotL, roughness);
            return ggx1 * ggx2;
        }

        void main() {
            vec3 N = normalize(Normal);
            vec3 V = normalize(viewPos - FragPos);

            vec3 F0 = vec3(1);
            F0 = mix(F0, albedo, metallic);

            vec3 Lo = vec3(0.0);

            for(int i = 0; i < numLights; i++) {
                vec3 L = normalize(lightPos[i] - FragPos);
                vec3 H = normalize(V + L);
                float distance = length(lightPos[i] - FragPos);
                float attenuation = 1.0 / (0.1 + distance * distance);  // Makes light fall-off slower
                vec3 radiance = lightColor[i] * attenuation;

                float NDF = DistributionGGX(N, H, roughness);
                float G = GeometrySmith(N, V, L, roughness);
                vec3 F = fresnelSchlick(clamp(dot(H, V), 0.0, 1.0), F0);

                vec3 numerator = NDF * G * F;
                float denominator = 4.0 * max(dot(N, V), 0.0) * max(dot(N, L), 0.0) + 0.0001;
                vec3 specular = numerator / denominator;

                vec3 kS = F;
                vec3 kD = vec3(1.0) - kS;
                kD *= 1.0 - metallic;

                float NdotL = max(dot(N, L), 0.0);
                Lo += (kD * albedo / PI + specular) * radiance * NdotL;
            }

            vec3 ambient = vec3(0.3) * albedo * ao;
            vec3 color = ambient + Lo;

            // Improved HDR tonemapping
            color = color / (color + vec3(1.0));

            // Gamma correction
            color = pow(color, vec3(1.0/2.2));

            // Debug coloring based on object type
            vec3 debug_color;
            if (roughness < 0.2) {
                debug_color = vec3(1.0, 0.0, 0.0);  // Red for very smooth objects (likely spheres)
            } else if (metallic > 0.8) {
                debug_color = vec3(0.0, 1.0, 0.0);  // Green for very metallic objects
            } else if (length(Normal) > 0.99) {
                debug_color = vec3(0.0, 0.0, 1.0);  // Blue for objects with consistent normals (like cubes)
            } else {
                debug_color = vec3(1.0, 1.0, 0.0);  // Yellow for other objects
            }
            if (length(color) < 0.001) {
                gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);  // Bright red for visibility
            } else {
                gl_FragColor = vec4(color, 1.0);
            }
        }
        """

    def compile(self):
        return compileProgram(compileShader(self.vertex_shader, GL_VERTEX_SHADER),
                            compileShader(self.fragment_shader, GL_FRAGMENT_SHADER))
