export default function CompaniesPage() {
  return (
    <div className="mx-auto max-w-3xl p-8">
      <h1 className="text-xl font-semibold text-neutral-50">Companies</h1>
      <p className="mt-2 text-sm text-neutral-400">
        Not implemented yet. This will list companies from the SQL tool&apos;s <code>companies</code> table
        (see scripts/seed_postgres.sql) once a live Postgres instance is seeded — no fake data shown in the
        meantime.
      </p>
    </div>
  );
}
