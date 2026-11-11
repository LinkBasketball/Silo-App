import { Link } from 'react-router-dom'
import { Compass } from 'lucide-react'
import { EmptyState } from '../components/ui'

export default function NotFound() {
  return <EmptyState icon={Compass} title="Page not found" action={<Link to="/" className="btn-primary">Back to News Intelligence</Link>}>The page you were looking for does not exist.</EmptyState>
}
