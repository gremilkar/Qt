// Copyright 2014 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef PlatformFederatedCredential_h
#define PlatformFederatedCredential_h

#include "platform/credentialmanager/PlatformCredential.h"
#include "platform/heap/Handle.h"
#include "wtf/text/WTFString.h"

namespace blink {

class PLATFORM_EXPORT PlatformFederatedCredential final : public PlatformCredential {
    WTF_MAKE_NONCOPYABLE(PlatformFederatedCredential);
public:
    static PlatformFederatedCredential* create(const String& id, const KURL& federation, const String& name, const KURL& avatarURL);
    virtual ~PlatformFederatedCredential();

    const KURL& federation() const { return m_federation; }

    virtual bool isFederated() override { return true; }

private:
    PlatformFederatedCredential(const String& id, const KURL& federation, const String& name, const KURL& avatarURL);

    KURL m_federation;
};

} // namespace blink

#endif // PlatformFederatedCredential_h
