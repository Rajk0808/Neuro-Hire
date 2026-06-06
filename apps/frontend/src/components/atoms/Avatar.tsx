export function Avatar({ name }: { name: string }) {
  const initials = name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2);

  return <div className="nh-avatar" aria-label={name}>{initials}</div>;
}
