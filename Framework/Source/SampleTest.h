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
#pragma once
#include "Falcor.h"

#define check_and_init_tests() if (mArgList.argExists("test")) { toggleText(false); initalizeTestingArgs(mArgList); }
#define check_and_run_tests() if(isTestingEnabled()) { runTestTask(frameRate()); }

using namespace Falcor;

class SampleTest
{
public:
    bool isTestingEnabled() const;
    void initalizeTestingArgs(const ArgList& args);
    void runTestTask(const FrameRate& frameRate);

private:
    void captureScreen();
    void outputXML();

    struct Task
    {
        enum class Type
        {
            LoadTime,
            MeasureFps,
            ScreenCapture,
            Shutdown,
            Uninitialized
        };

        Task() : mStartFrame(0u), mEndFrame(0u), mTask(Type::Uninitialized), mResult(0.f) {}
        Task(uint32_t startFrame, uint32_t endFrame, Task::Type t) :
            mStartFrame(startFrame), mEndFrame(endFrame), mTask(t), mResult(0.f) {}
        bool operator<(const Task& rhs) { return mStartFrame < rhs.mStartFrame; }

        uint32_t mStartFrame;
        uint32_t mEndFrame;
        Type mTask;
        float mResult = 0;
    };

    std::vector<Task> mTestTasks;
    std::vector<Task>::iterator mTestTaskIt;
};