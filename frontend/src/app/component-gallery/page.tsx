import { notFound } from "next/navigation";
import ComponentGalleryClient from "./ComponentGalleryClient";

export default function Page() {
  const enabled =
    process.env.NODE_ENV === "development" ||
    process.env.NEXT_PUBLIC_ENABLE_COMPONENT_GALLERY === "true";

  if (!enabled) notFound();

  return <ComponentGalleryClient />;
}
