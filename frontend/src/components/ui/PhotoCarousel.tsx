import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import type { IdmsInventoryPhoto } from '@/types/idms'

interface PhotoCarouselProps {
  photos: IdmsInventoryPhoto[]
  alt?: string
}

export default function PhotoCarousel({ photos, alt = 'Vehículo' }: PhotoCarouselProps) {
  const [index, setIndex] = useState(0)
  const [lightboxOpen, setLightboxOpen] = useState(false)

  if (photos.length === 0) {
    return <span className="text-gray-400">—</span>
  }

  const prev = (e?: React.MouseEvent) => {
    e?.stopPropagation()
    setIndex((i) => (i - 1 + photos.length) % photos.length)
  }
  const next = (e?: React.MouseEvent) => {
    e?.stopPropagation()
    setIndex((i) => (i + 1) % photos.length)
  }

  return (
    <>
      <div className="relative w-24">
        <button
          type="button"
          onClick={() => setLightboxOpen(true)}
          className="block overflow-hidden rounded border border-gray-200 bg-gray-50"
        >
          <img
            src={photos[index].thumbnail_url}
            alt={alt}
            className="h-16 w-24 object-cover transition-opacity hover:opacity-80"
            loading="lazy"
          />
        </button>
        {photos.length > 1 && (
          <>
            <button
              type="button"
              onClick={prev}
              aria-label="Foto anterior"
              className="absolute left-0 top-1/2 -translate-y-1/2 rounded-full bg-black/50 px-1.5 py-0.5 text-xs text-white hover:bg-black/70"
            >
              ‹
            </button>
            <button
              type="button"
              onClick={next}
              aria-label="Foto siguiente"
              className="absolute right-0 top-1/2 -translate-y-1/2 rounded-full bg-black/50 px-1.5 py-0.5 text-xs text-white hover:bg-black/70"
            >
              ›
            </button>
            <span className="mt-0.5 block text-center text-[10px] text-gray-500">
              {index + 1}/{photos.length}
            </span>
          </>
        )}
      </div>

      {lightboxOpen && (
        <PhotoLightbox
          photos={photos}
          index={index}
          alt={alt}
          onIndexChange={setIndex}
          onClose={() => setLightboxOpen(false)}
        />
      )}
    </>
  )
}

interface PhotoLightboxProps {
  photos: IdmsInventoryPhoto[]
  index: number
  alt: string
  onIndexChange: (i: number) => void
  onClose: () => void
}

function PhotoLightbox({ photos, index, alt, onIndexChange, onClose }: PhotoLightboxProps) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
      if (e.key === 'ArrowLeft') onIndexChange((index - 1 + photos.length) % photos.length)
      if (e.key === 'ArrowRight') onIndexChange((index + 1) % photos.length)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [index, photos.length, onIndexChange, onClose])

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-6"
      onClick={onClose}
    >
      <button
        type="button"
        onClick={onClose}
        aria-label="Cerrar"
        className="absolute right-5 top-5 text-3xl font-light text-white/80 hover:text-white"
      >
        ×
      </button>

      <div className="relative flex max-h-full max-w-4xl items-center" onClick={(e) => e.stopPropagation()}>
        {photos.length > 1 && (
          <button
            type="button"
            onClick={() => onIndexChange((index - 1 + photos.length) % photos.length)}
            aria-label="Foto anterior"
            className="absolute left-0 -translate-x-full px-3 text-4xl font-light text-white/80 hover:text-white"
          >
            ‹
          </button>
        )}

        <img
          src={photos[index].image_url}
          alt={alt}
          className="max-h-[80vh] max-w-full rounded-md object-contain shadow-2xl"
        />

        {photos.length > 1 && (
          <button
            type="button"
            onClick={() => onIndexChange((index + 1) % photos.length)}
            aria-label="Foto siguiente"
            className="absolute right-0 translate-x-full px-3 text-4xl font-light text-white/80 hover:text-white"
          >
            ›
          </button>
        )}
      </div>

      {photos.length > 1 && (
        <span className="absolute bottom-6 text-sm text-white/80">
          {index + 1} / {photos.length}
        </span>
      )}
    </div>,
    document.body,
  )
}
