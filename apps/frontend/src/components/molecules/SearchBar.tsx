import { Search } from "lucide-react";

export function SearchBar() {
  return (
    <label className="search-bar">
      <Search size={18} />
      <input placeholder="Search talent, roles, skills, agents..." />
    </label>
  );
}
