export function Landing({ onStart }: { onStart: () => void }) {
  return (
    <div className="landing">
      <section className="hero-section">
        <div>
          <p className="eyebrow">Operação condominial sem ruído</p>
          <h1>O síndico não deveria administrar um condomínio pelo WhatsApp.</h1>
          <p>
            Kondo transforma chamados, inadimplência, comunicados, documentos e decisões do condomínio em uma operação
            clara, rastreável e guiada por IA.
          </p>
          <div className="landing-actions">
            <button className="btn btn-primary" type="button" onClick={onStart}>
              Ver demo do Kondo
            </button>
            <a className="btn btn-outline" href="#" onClick={(event) => event.preventDefault()}>
              Explorar painel
            </a>
          </div>
        </div>
        <div className="hero-card">
          <p className="hero-kicker">Painel operacional</p>
          <h3>Condomínio Jardim Aurora</h3>
          <p>12 chamados abertos</p>
          <p>2 críticos</p>
          <p>Gap de caixa: R$ -2.160</p>
          <p>Inadimplência: 11,95%</p>
        </div>
      </section>

      <section className="panel">
        <h2>Números que importam</h2>
        <div className="stats-grid">
          <article className="stat">
            <p>327 mil</p>
            <span>condomínios no Brasil</span>
          </article>
          <article className="stat">
            <p>39 milhões</p>
            <span>moradores</span>
          </article>
          <article className="stat">
            <p>11,95%</p>
            <span>inadimplência acima de 30 dias</span>
          </article>
          <article className="stat">
            <p>308 mil+</p>
            <span>chamados registrados em 2025</span>
          </article>
        </div>
      </section>

      <section className="panel grid-cols-2">
        <div>
          <h2>Problema</h2>
          <ul>
            <li>Chamados somem no WhatsApp</li>
            <li>Financeiro chega tarde</li>
            <li>Documentos ficam enterrados</li>
            <li>Conselho enxerga pouco</li>
          </ul>
        </div>
        <div>
          <h2>Solução</h2>
          <ul>
            <li>Dashboard de prioridades</li>
            <li>Kanban operacional</li>
            <li>Chamados inteligentes</li>
            <li>Financeiro e acordos</li>
            <li>Documentos com IA</li>
            <li>Comunicados prontos</li>
            <li>Portal do morador</li>
          </ul>
        </div>
      </section>

      <section className="panel">
        <h2>Fluxo da operação</h2>
        <p>Morador abre chamado ? IA classifica ? Kanban cria execução ? fornecedor é acionado ? morador acompanha status.</p>
      </section>

      <section className="cta-final panel">
        <p>Seu condomínio já tem dados. Falta transformar isso em decisão.</p>
        <button className="btn btn-primary" type="button" onClick={onStart}>
          Começar demo
        </button>
      </section>
    </div>
  )
}

