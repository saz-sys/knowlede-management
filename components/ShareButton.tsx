"use client";

import { useState, useRef, useEffect } from "react";

interface ShareButtonProps {
  postId: string;
  postTitle: string;
}

export default function ShareButton({ postId, postTitle }: ShareButtonProps) {
  const [isCopied, setIsCopied] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [dropdownRect, setDropdownRect] = useState<{ top: number; left: number; width: number }>({
    top: 0,
    left: 0,
    width: 0,
  });
  const buttonRef = useRef<HTMLButtonElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const publicUrl = `${window.location.origin}/posts/${postId}/public`;
  const shareText = `${postTitle} - Tech Reef`;

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(publicUrl);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy link:', err);
    }
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: postTitle,
          text: shareText,
          url: publicUrl,
        });
      } catch (err) {
        console.error('Failed to share:', err);
      }
    } else {
      // フォールバック: クリップボードにコピー
      handleCopyLink();
    }
  };

  // ドロップダウンの位置を計算
  useEffect(() => {
    if (!isOpen || !buttonRef.current) {
      return;
    }

    const margin = 16;

    const updatePosition = () => {
      if (!buttonRef.current) return;

      const buttonRect = buttonRef.current.getBoundingClientRect();
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;
      const width = Math.min(320, viewportWidth - margin * 2);
      const centeredLeft = buttonRect.left + buttonRect.width / 2 - width / 2;
      const clampedLeft = Math.min(Math.max(centeredLeft, margin), viewportWidth - margin - width);
      const top = Math.min(buttonRect.bottom + 8, viewportHeight - margin - 20);

      setDropdownRect({ top, left: clampedLeft, width });
    };

    updatePosition();

    window.addEventListener("resize", updatePosition);
    window.addEventListener("scroll", updatePosition, true);

    return () => {
      window.removeEventListener("resize", updatePosition);
      window.removeEventListener("scroll", updatePosition, true);
    };
  }, [isOpen]);

  // クリック外部で閉じる
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        buttonRef.current &&
        !buttonRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  return (
    <div className="relative">
      <button
        ref={buttonRef}
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        <svg
          className="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z"
          />
        </svg>
        共有
      </button>

      {isOpen && (
        <div
          ref={dropdownRef}
          style={{
            position: "fixed",
            top: dropdownRect.top,
            left: dropdownRect.left,
            width: dropdownRect.width || 280,
            maxWidth: "calc(100vw - 2rem)",
          }}
          className="z-50 bg-white rounded-lg shadow-lg border border-gray-200 p-4"
        >
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                共有リンク
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={publicUrl}
                  readOnly
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm bg-gray-50"
                />
                <button
                  onClick={handleCopyLink}
                  className={`px-3 py-2 text-sm rounded-md transition-colors ${
                    isCopied
                      ? 'bg-green-100 text-green-700'
                      : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                  }`}
                >
                  {isCopied ? 'コピー済み' : 'コピー'}
                </button>
              </div>
            </div>

            <div className="border-t border-gray-200 pt-3">
              <button
                onClick={handleShare}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z"
                  />
                </svg>
                ネイティブ共有
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
