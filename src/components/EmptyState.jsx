export default function EmptyState({ title, message, action }) {
  return (
    <div className="empty-state">
      <h3>{title}</h3>
      <p>{message}</p>
      {action ? <button className="btn btn-primary" type="button" onClick={action.onClick}>{action.label}</button> : null}
    </div>
  );
}
