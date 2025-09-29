"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

interface AutoRedirectProps {
  to: string;
  delay?: number;
}

export default function AutoRedirect({ to, delay = 0 }: AutoRedirectProps) {
  const router = useRouter();

  useEffect(() => {
    const timer = setTimeout(() => {
      router.replace(to);
    }, delay);

    return () => clearTimeout(timer);
  }, [router, to, delay]);

  useEffect(() => {
    const timer = setTimeout(() => {
      window.location.replace(to);
    }, delay);

    return () => clearTimeout(timer);
  }, [to, delay]);

  return null;
}

