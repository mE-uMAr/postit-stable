import type { IconType } from "react-icons";
import {
  FaXTwitter,
  FaLinkedinIn,
  FaInstagram,
  FaThreads,
  FaFacebookF,
  FaTiktok,
  FaYoutube,
  FaWordpress,
  FaBloggerB,
} from "react-icons/fa6";
import type { PlatformKey } from "@/lib/types";

/**
 * Real brand marks for each platform, rendered with `currentColor` so they
 * inherit the white-on-brand-color treatment of the surrounding `.pf` chip.
 * Sizing is handled by the `.pf-logo` CSS class (a fraction of the chip).
 */
const LOGOS: Record<PlatformKey, IconType> = {
  x: FaXTwitter,
  linkedin: FaLinkedinIn,
  instagram: FaInstagram,
  threads: FaThreads,
  facebook: FaFacebookF,
  tiktok: FaTiktok,
  youtube: FaYoutube,
  wordpress: FaWordpress,
  blogger: FaBloggerB,
};

interface PlatformLogoProps {
  platform: PlatformKey;
  className?: string;
}

export function PlatformLogo({ platform, className = "pf-logo" }: PlatformLogoProps) {
  const Logo = LOGOS[platform];
  return <Logo className={className} aria-hidden focusable={false} />;
}
