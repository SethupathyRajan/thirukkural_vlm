import React from 'react';

interface AvatarProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src?: string;
  alt?: string;
  size?: number;
  fallback?: string; // Initials or icons
}

const Avatar: React.FC<AvatarProps> = ({
  src,
  alt,
  size = 40,
  fallback,
  className,
  ...props
}) => {
  return (
    <div
      className={`relative flex h-[${size}px] w-[${size}px] shrink-0 overflow-hidden rounded-full`}
      {...props}
    >
      {src ? (
        <img
          src={src}
          alt={alt ?? ''}
          className="aspect-square h-full w-full object-cover"
        />
      ) : (
        <div className="flex flex-col items-center justify-center bg-primary text-primary-foreground text-xs font-medium">
          {fallback?.slice(0, 2).toUpperCase()}
        </div>
      )}
    </div>
  );
};

export { Avatar };
export default Avatar;