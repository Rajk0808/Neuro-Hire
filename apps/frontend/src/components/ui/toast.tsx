export function Toast({ message }: { message: string }) {
  return <div className="panel toast-shell">{message}</div>;
}
