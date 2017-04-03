/***************************************************************************
# Copyright (c) 2015, NVIDIA CORPORATION. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#  * Neither the name of NVIDIA CORPORATION nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
***************************************************************************/
#version 450
#include "HlslGlslCommon.h"

UNIFORM_BUFFER(PerImageCB, 0)
{
#ifdef _USE_2D_ARRAY
	sampler2DArray gTexture;
#else
   sampler2D gTexture;
#endif
    int cascade;
};

vec4 calcColor(vec2 texC)
{
#ifdef _USE_2D_ARRAY
	float d = textureLod(gTexture, vec3(texC, float(cascade)), 0).r;
#else
    float d = textureLod(gTexture, texC, 0).r;
#endif
    return vec4(d.xxx, 1);
}

#ifdef FALCOR_HLSL
vec4 main(float2 texC  : TEXCOORD) : SV_TARGET0
{
	return calcColor(texC);
}

#elif defined FALCOR_GLSL
in vec2 texC;
out vec4 fragColor;

void main()
{
	fragColor = calcColor(texC);
}
#endif