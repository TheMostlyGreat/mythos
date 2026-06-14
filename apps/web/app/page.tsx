"use client";

import { useState } from "react";

const forkChoices = [
  {
    title: "Make it intimate",
    tradeoff: "Smaller stakes, sharper wound.",
    effect:
      "The detective’s gift exposes the memory she is trying not to relive.",
    preview:
      "The corpse was still warm when Mara touched the wedding ring and remembered saying yes to a man she had never met. By the time she pulled her hand away, the victim’s last breath was gone from the room — and so was the sound of her own mother’s laugh.",
  },
  {
    title: "Make it dangerous",
    tradeoff: "The premise starts costing someone immediately.",
    effect:
      "The first memory she reads makes her an accomplice before she understands the crime.",
    preview:
      "Mara read the dead man’s final memory and saw herself in it, standing across the alley with a knife she did not own. The police sirens were three blocks away. The memory was already replacing her alibi.",
  },
  {
    title: "Make it strange",
    tradeoff: "The world bends around the central contradiction.",
    effect:
      "Memories leave physical bruises, and every witness carries evidence on their skin.",
    preview:
      "The victim’s last memory bloomed across Mara’s wrist in a purple ring of teeth marks. Across the precinct, every witness began covering their arms, hiding the parts of the truth their bodies had kept.",
  },
];

export default function HomePage() {
  const [selectedFork, setSelectedFork] = useState(0);
  const activeFork = forkChoices[selectedFork] ?? forkChoices[0]!;

  return (
    <main className="app-shell" aria-labelledby="page-title">
      <aside className="story-rail" aria-label="Story map">
        <p className="eyebrow">Mythos</p>
        <nav>
          <a href="#premise">Premise</a>
          <a href="#proof">Authored proof</a>
          <a href="#forks">First turn</a>
          <a href="#opening">Opening scene</a>
        </nav>
      </aside>

      <section className="story-canvas">
        <div className="hero" id="premise">
          <p className="eyebrow eyebrow-on-paper">First-minute prototype</p>
          <h1 id="page-title">What story won’t leave you alone?</h1>
          <p className="lede">
            Give Mythos the image, contradiction, or character you keep
            circling. You will steer before anything long is written.
          </p>
          <div className="premise-box" aria-label="Example premise">
            A detective can see people’s memories, but every memory she reads
            replaces one of her own.
          </div>
          <button type="button">Find the story</button>
        </div>

        <article className="manuscript-card" id="proof">
          <p className="eyebrow eyebrow-on-paper">Authored proof</p>
          <h2>Here’s the pressure point Mythos sees</h2>
          <p>
            This is not really a mystery about finding the killer. It is a story
            about a woman who can solve any crime except the one happening
            inside her: every act of empathy makes her less certain which griefs
            are hers.
          </p>
        </article>

        <article
          className="manuscript-card mutation"
          id="opening"
          aria-labelledby="opening-title"
          aria-live="polite"
        >
          <p className="eyebrow eyebrow-on-paper">Visible mutation</p>
          <h2 id="opening-title">Opening-scene preview</h2>
          <p className="choice-callback">
            Chosen fork: <strong>{activeFork.title}</strong> —{" "}
            {activeFork.effect}
          </p>
          <p>{activeFork.preview}</p>
        </article>
      </section>

      <aside className="living-margin" id="forks" aria-label="Living margin">
        <p className="eyebrow">Choose the first turn</p>
        <h2>Three directions, three costs</h2>
        <div className="fork-list" role="list">
          {forkChoices.map((choice, index) => {
            const isSelected = selectedFork === index;

            return (
              <button
                aria-pressed={isSelected}
                className="fork-card"
                key={choice.title}
                onClick={() => setSelectedFork(index)}
                type="button"
              >
                <span aria-hidden="true">0{index + 1}</span>
                <h3>{choice.title}</h3>
                <p>{choice.tradeoff}</p>
                <small>{choice.effect}</small>
              </button>
            );
          })}
        </div>
        <p className="canon-note">
          Your selected fork becomes canon. Mythos shows where the choice lands
          before it asks for another one.
        </p>
      </aside>
    </main>
  );
}
