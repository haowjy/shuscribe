import { redirect } from "next/navigation";

export default function Page() {
  // Redirect to the first editor variant
  redirect("/component-gallery/editor/full");
}
